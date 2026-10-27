"""Dagster assets: download the datasets, then build the warehouse.

Run once:      make pipeline         (python -m pipeline)
Browse in UI:  make dagster          (dagster dev)
"""

import httpx
from dagster import Definitions, MaterializeResult, asset

from pipeline.build import build_warehouse
from pipeline.olist import OLIST_TABLES, download_olist, extract_olist, kaggle_auth
from pipeline.settings import PipelineSettings
from pipeline.weather import download_weather, read_weather


def http_client() -> httpx.Client:
    return httpx.Client(
        timeout=120,
        transport=httpx.HTTPTransport(retries=3),
        headers={"User-Agent": "ai-data-analyst-pipeline"},
    )


@asset(group_name="ingestion", description="Olist zip from Kaggle, extracted to CSVs.")
def olist_files() -> MaterializeResult[None]:
    settings = PipelineSettings.from_env()
    auth = kaggle_auth(settings.kaggle_username, settings.kaggle_key)
    with http_client() as client:
        result = download_olist(client, settings.raw_dir, auth)
    paths = extract_olist(result.path, settings.raw_dir / "olist" / "csv")
    return MaterializeResult(
        metadata={
            "sha256": result.sha256,
            "skipped_download": result.skipped,
            "csv_files": len(paths),
        }
    )


@asset(group_name="ingestion", description="Daily weather JSON per state capital (Open-Meteo).")
def weather_files() -> MaterializeResult[None]:
    settings = PipelineSettings.from_env()
    with http_client() as client:
        results = download_weather(client, settings.raw_dir)
    skipped = sum(result.skipped for result in results)
    return MaterializeResult(metadata={"files": len(results), "skipped_downloads": skipped})


@asset(
    group_name="warehouse",
    deps=[olist_files, weather_files],
    description="DuckDB warehouse: raw tables + dbt build, swapped in atomically.",
)
def warehouse() -> MaterializeResult[None]:
    settings = PipelineSettings.from_env()
    csv_dir = settings.raw_dir / "olist" / "csv"
    csvs = {table: csv_dir / filename for table, filename in OLIST_TABLES.items()}
    counts = build_warehouse(settings.warehouse_path, csvs, read_weather(settings.raw_dir))
    return MaterializeResult(
        metadata={"path": str(settings.warehouse_path)}
        | {f"rows.{table}": count for table, count in counts.items()}
    )


defs = Definitions(assets=[olist_files, weather_files, warehouse])
