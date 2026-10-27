"""Mart-level checks on the synthetic fixture warehouse."""

import json
from pathlib import Path

import duckdb
import pytest

from pipeline.settings import DBT_DIR

MARTS = [
    "dim_customers",
    "dim_date",
    "dim_geography",
    "dim_products",
    "dim_sellers",
    "fct_daily_weather",
    "fct_order_items",
    "fct_orders",
    "fct_payments",
    "fct_reviews",
]
REGIONAL_TABLES = [
    "dim_customers",
    "dim_sellers",
    "fct_daily_weather",
    "fct_order_items",
    "fct_orders",
    "fct_payments",
    "fct_reviews",
]
REGIONS = {"Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"}


def query(warehouse: Path, sql: str) -> list[tuple[object, ...]]:
    with duckdb.connect(str(warehouse), read_only=True) as con:
        return con.execute(sql).fetchall()


def scalar(warehouse: Path, sql: str) -> object:
    return query(warehouse, sql)[0][0]


def mart_columns(warehouse: Path) -> dict[str, list[str]]:
    rows = query(
        warehouse,
        "select table_name, column_name from information_schema.columns "
        "where table_schema = 'marts' order by table_name, ordinal_position",
    )
    columns: dict[str, list[str]] = {}
    for table, column in rows:
        columns.setdefault(str(table), []).append(str(column))
    return columns


def test_marts_schema_has_exactly_the_planned_tables(fixture_warehouse: Path) -> None:
    assert sorted(mart_columns(fixture_warehouse)) == MARTS


@pytest.mark.parametrize("mart", MARTS)
def test_mart_has_rows(fixture_warehouse: Path, mart: str) -> None:
    assert scalar(fixture_warehouse, f"select count(*) from marts.{mart}") > 0  # type: ignore[operator]


def test_every_mart_column_has_a_description(fixture_warehouse: Path) -> None:
    manifest = json.loads((DBT_DIR / "target" / "manifest.json").read_text())
    documented = {
        node["name"]: {name for name, col in node["columns"].items() if col.get("description")}
        for node in manifest["nodes"].values()
        if node["resource_type"] == "model" and node["schema"] == "marts"
    }

    missing = [
        f"{table}.{column}"
        for table, columns in mart_columns(fixture_warehouse).items()
        for column in columns
        if column not in documented.get(table, set())
    ]

    assert missing == []


@pytest.mark.parametrize("table", REGIONAL_TABLES)
def test_regional_tables_have_a_valid_region_on_every_row(
    fixture_warehouse: Path, table: str
) -> None:
    regions = {
        row[0] for row in query(fixture_warehouse, f"select distinct region from marts.{table}")
    }
    assert regions <= REGIONS
    assert None not in regions


def test_fct_orders_is_one_row_per_order(fixture_warehouse: Path) -> None:
    facts = scalar(fixture_warehouse, "select count(*) from marts.fct_orders")
    source = scalar(fixture_warehouse, "select count(*) from staging.stg_olist__orders")
    assert facts == source


def test_order_items_do_not_fan_out(fixture_warehouse: Path) -> None:
    facts = scalar(fixture_warehouse, "select sum(price) from marts.fct_order_items")
    source = scalar(fixture_warehouse, "select sum(price) from staging.stg_olist__order_items")
    assert facts == source


def test_order_value_matches_its_items(fixture_warehouse: Path) -> None:
    orders = scalar(fixture_warehouse, "select sum(order_value) from marts.fct_orders")
    items = scalar(fixture_warehouse, "select sum(item_value) from marts.fct_order_items")
    assert orders == items


def test_orders_without_items_have_zero_value_not_null(fixture_warehouse: Path) -> None:
    rows = query(
        fixture_warehouse,
        "select item_count, order_value from marts.fct_orders where order_status = 'unavailable'",
    )
    assert rows
    assert all(row == (0, 0) for row in rows)


def test_reviews_are_one_per_order(fixture_warehouse: Path) -> None:
    dupes = scalar(
        fixture_warehouse,
        "select count(*) - count(distinct order_id) from marts.fct_reviews",
    )
    assert dupes == 0


def test_customers_are_one_row_per_person(fixture_warehouse: Path) -> None:
    people = scalar(
        fixture_warehouse,
        "select count(distinct customer_unique_id) from staging.stg_olist__customers",
    )
    assert scalar(fixture_warehouse, "select count(*) from marts.dim_customers") == people
    assert scalar(
        fixture_warehouse, "select count(*) from marts.dim_customers where is_repeat_customer"
    )


def test_untranslated_and_missing_categories_get_a_label(fixture_warehouse: Path) -> None:
    labels = {
        row[0]
        for row in query(fixture_warehouse, "select distinct category from marts.dim_products")
    }
    assert None not in labels
    assert {"pc_gamer", "unknown", "health_beauty"} <= labels


def test_delivery_days_are_never_negative(fixture_warehouse: Path) -> None:
    assert scalar(
        fixture_warehouse, "select count(*) from marts.fct_orders where delivery_days < 0"
    ) == 0


def test_dim_date_covers_the_order_period_and_flags_black_friday(fixture_warehouse: Path) -> None:
    first, last = query(fixture_warehouse, "select min(date_day), max(date_day) from marts.dim_date")[0]
    black_fridays = query(
        fixture_warehouse, "select date_day from marts.dim_date where is_black_friday order by 1"
    )
    assert str(first) == "2016-09-01"
    assert str(last) == "2018-10-31"
    assert [str(row[0]) for row in black_fridays] == ["2016-11-25", "2017-11-24"]


def test_marts_do_not_expose_free_text_review_comments(fixture_warehouse: Path) -> None:
    columns = {c for cols in mart_columns(fixture_warehouse).values() for c in cols}
    assert not {"comment_title", "comment_message"} & columns


def test_delivery_metrics_only_for_delivered_orders(fixture_warehouse: Path) -> None:
    assert scalar(
        fixture_warehouse,
        "select count(*) from marts.fct_orders "
        "where order_status != 'delivered' and (delivery_days is not null or is_late is not null)",
    ) == 0
