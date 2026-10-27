"""Build the warehouse: load raw tables, run dbt, swap the file in atomically."""

from pathlib import Path

import duckdb

from pipeline.dbt import run_dbt
from pipeline.load import WEATHER_TABLE, load_csv_table, load_weather_table
from pipeline.warehouse import atomic_build
from pipeline.weather import WeatherRow


def load_raw(
    warehouse_path: Path, olist_csvs: dict[str, Path], weather_rows: list[WeatherRow]
) -> dict[str, int]:
    """Load every raw table and return row counts by table name."""
    counts: dict[str, int] = {}
    with duckdb.connect(str(warehouse_path)) as con:
        for table, csv_path in olist_csvs.items():
            counts[f"olist_{table}"] = load_csv_table(con, table, csv_path)
        counts[WEATHER_TABLE] = load_weather_table(con, weather_rows)
    return counts


def build_warehouse(
    warehouse_path: Path,
    olist_csvs: dict[str, Path],
    weather_rows: list[WeatherRow],
    *,
    dbt_select: str | None = None,
) -> dict[str, int]:
    """Build a fresh warehouse at `warehouse_path`. The old file is kept if anything fails."""
    dbt_args = ["build"] + (["--select", dbt_select] if dbt_select else [])
    with atomic_build(warehouse_path) as tmp:
        counts = load_raw(tmp, olist_csvs, weather_rows)
        empty = [table for table, count in counts.items() if count == 0]
        if empty:
            raise ValueError(f"Raw tables are empty: {', '.join(empty)}")
        run_dbt(dbt_args, tmp)
    return counts
