"""Shared fixtures. `fixture_warehouse` is built once per test session."""

from pathlib import Path

import pytest

from pipeline.build import build_warehouse
from tests.fixtures.synthetic import generate, write_csvs


@pytest.fixture(scope="session")
def fixture_warehouse(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A warehouse built from synthetic Olist-shaped data by the real pipeline code."""
    root = tmp_path_factory.mktemp("warehouse")
    data = generate()
    csvs = write_csvs(data, root / "csv")
    warehouse = root / "warehouse.duckdb"
    build_warehouse(warehouse, csvs, data.weather)
    return warehouse
