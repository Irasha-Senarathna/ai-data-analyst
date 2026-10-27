import time
from pathlib import Path

import duckdb
import pytest

from pipeline.build import build_warehouse
from tests.fixtures.synthetic import generate, write_csvs

STAGING_MODELS = [
    "stg_olist__orders",
    "stg_olist__order_items",
    "stg_olist__order_payments",
    "stg_olist__order_reviews",
    "stg_olist__customers",
    "stg_olist__sellers",
    "stg_olist__products",
    "stg_olist__category_translation",
    "stg_olist__geolocation",
    "stg_open_meteo__weather_daily",
]


def scalar(warehouse: Path, sql: str) -> object:
    with duckdb.connect(str(warehouse), read_only=True) as con:
        row = con.execute(sql).fetchone()
    assert row is not None
    return row[0]


def test_fixture_warehouse_builds_in_under_ten_seconds(tmp_path: Path) -> None:
    data = generate()
    csvs = write_csvs(data, tmp_path / "csv")

    started = time.perf_counter()
    counts = build_warehouse(tmp_path / "warehouse.duckdb", csvs, data.weather)
    elapsed = time.perf_counter() - started

    assert elapsed < 10, f"fixture build took {elapsed:.1f}s"
    assert all(count > 0 for count in counts.values())
    assert len(counts) == 10


@pytest.mark.parametrize("model", STAGING_MODELS)
def test_staging_model_has_rows(fixture_warehouse: Path, model: str) -> None:
    assert scalar(fixture_warehouse, f"select count(*) from staging.{model}") > 0  # type: ignore[operator]


def test_reviews_keep_both_orders_of_a_shared_review(fixture_warehouse: Path) -> None:
    shared = scalar(
        fixture_warehouse,
        "select count(*) from (select review_id from staging.stg_olist__order_reviews "
        "group by review_id having count(*) > 1)",
    )
    assert shared == 1


def test_geolocation_is_one_row_per_zip_prefix_inside_brazil(fixture_warehouse: Path) -> None:
    max_lat = scalar(fixture_warehouse, "select max(latitude) from staging.stg_olist__geolocation")
    dupes = scalar(
        fixture_warehouse,
        "select count(*) - count(distinct zip_code_prefix) from staging.stg_olist__geolocation",
    )
    assert dupes == 0
    assert max_lat < 6  # type: ignore[operator]


def test_typed_columns(fixture_warehouse: Path) -> None:
    with duckdb.connect(str(fixture_warehouse), read_only=True) as con:
        types = dict(
            con.execute(
                "select column_name, data_type from information_schema.columns "
                "where table_schema = 'staging' and table_name = 'stg_olist__order_items'"
            ).fetchall()
        )
    assert types["price"] == "DECIMAL(12,2)"
    assert types["shipping_limit_at"] == "TIMESTAMP"
    assert types["order_item_number"] == "INTEGER"


def test_failed_dbt_build_keeps_previous_warehouse(tmp_path: Path) -> None:
    data = generate(orders=50)
    csvs = write_csvs(data, tmp_path / "csv")
    warehouse = tmp_path / "warehouse.duckdb"
    build_warehouse(warehouse, csvs, data.weather)
    before = warehouse.stat().st_mtime_ns

    bad_state = csvs["customers"].read_text().replace(",SP\n", ",XX\n", 1)
    csvs["customers"].write_text(bad_state)
    with pytest.raises(RuntimeError):
        build_warehouse(warehouse, csvs, data.weather)

    assert warehouse.stat().st_mtime_ns == before
