"""Load downloaded files into the `raw` schema of DuckDB.

Every Olist column is loaded as text; dbt staging models do the typing, so
values like zip prefixes keep their leading zeros.

Table names are interpolated into SQL only from module constants or the
OLIST_TABLES allow-list (hence the S608 suppressions); values are bound as
parameters.
"""

from pathlib import Path

import duckdb

from pipeline.olist import OLIST_TABLES
from pipeline.weather import WeatherRow

RAW_SCHEMA = "raw"
WEATHER_TABLE = "open_meteo_weather_daily"


def ensure_raw_schema(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(f"create schema if not exists {RAW_SCHEMA}")


def count_rows(con: duckdb.DuckDBPyConnection, table: str) -> int:
    row = con.execute(f"select count(*) from {RAW_SCHEMA}.{table}").fetchone()  # noqa: S608
    return int(row[0]) if row else 0


def load_csv_table(con: duckdb.DuckDBPyConnection, table: str, csv_path: Path) -> int:
    """Create raw.olist_<table> from a CSV and return its row count."""
    if table not in OLIST_TABLES:
        raise ValueError(f"Unknown Olist table: {table!r}")
    ensure_raw_schema(con)
    raw_table = f"olist_{table}"
    con.execute(
        f"create or replace table {RAW_SCHEMA}.{raw_table} as "  # noqa: S608
        "select * from read_csv(?, header = true, all_varchar = true)",
        [str(csv_path)],
    )
    return count_rows(con, raw_table)


def load_weather_table(con: duckdb.DuckDBPyConnection, rows: list[WeatherRow]) -> int:
    """Create raw.open_meteo_weather_daily and return its row count."""
    ensure_raw_schema(con)
    con.execute(
        f"create or replace table {RAW_SCHEMA}.{WEATHER_TABLE} ("
        "state varchar, weather_date date, temperature_2m_max double, "
        "temperature_2m_min double, precipitation_sum double)"
    )
    con.executemany(
        f"insert into {RAW_SCHEMA}.{WEATHER_TABLE} values (?, ?, ?, ?, ?)",  # noqa: S608
        [
            (
                row.state,
                row.weather_date,
                row.temperature_2m_max,
                row.temperature_2m_min,
                row.precipitation_sum,
            )
            for row in rows
        ],
    )
    return count_rows(con, WEATHER_TABLE)
