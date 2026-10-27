from datetime import date
from pathlib import Path

import duckdb
import pytest

from pipeline.load import load_csv_table, load_weather_table
from pipeline.weather import WeatherRow


def test_load_csv_table_creates_raw_table_with_all_text_columns(tmp_path: Path) -> None:
    csv_path = tmp_path / "customers.csv"
    csv_path.write_text("customer_id,customer_zip_code_prefix\na,01001\nb,02002\n")
    con = duckdb.connect()

    row_count = load_csv_table(con, "customers", csv_path)

    assert row_count == 2
    types = con.execute(
        "select data_type from information_schema.columns "
        "where table_schema = 'raw' and table_name = 'olist_customers'"
    ).fetchall()
    assert types == [("VARCHAR",), ("VARCHAR",)]
    # leading zeros survive because nothing is type-guessed at load time
    assert con.execute(
        "select customer_zip_code_prefix from raw.olist_customers order by 1"
    ).fetchall() == [("01001",), ("02002",)]


def test_load_csv_table_rejects_unknown_table(tmp_path: Path) -> None:
    con = duckdb.connect()

    with pytest.raises(ValueError, match="Unknown Olist table"):
        load_csv_table(con, "customers; drop table x", tmp_path / "x.csv")


def test_load_weather_table(tmp_path: Path) -> None:
    con = duckdb.connect()
    rows = [
        WeatherRow("SP", date(2017, 1, 1), 30.0, 20.0, 0.0),
        WeatherRow("RJ", date(2017, 1, 1), 33.0, None, 5.5),
    ]

    row_count = load_weather_table(con, rows)

    assert row_count == 2
    assert con.execute(
        "select state, precipitation_sum from raw.open_meteo_weather_daily order by state"
    ).fetchall() == [("RJ", 5.5), ("SP", 0.0)]
