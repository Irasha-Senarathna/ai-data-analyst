from pathlib import Path

import pytest

from pipeline.warehouse import atomic_build, temp_path_for


def test_successful_build_replaces_the_warehouse(tmp_path: Path) -> None:
    final = tmp_path / "warehouse.duckdb"
    final.write_text("old")

    with atomic_build(final) as tmp:
        tmp.write_text("new")

    assert final.read_text() == "new"
    assert not tmp.exists()


def test_failed_build_keeps_the_old_warehouse(tmp_path: Path) -> None:
    final = tmp_path / "warehouse.duckdb"
    final.write_text("old")

    with pytest.raises(RuntimeError), atomic_build(final) as tmp:
        tmp.write_text("half-built")
        raise RuntimeError("dbt failed")

    assert final.read_text() == "old"
    assert not tmp.exists()


def test_build_starts_from_an_empty_temp_file(tmp_path: Path) -> None:
    final = tmp_path / "warehouse.duckdb"
    leftover = temp_path_for(final)
    leftover.parent.mkdir()
    leftover.write_text("leftover from a crash")

    with atomic_build(final) as tmp:
        assert not tmp.exists()
        tmp.write_text("new")

    assert final.read_text() == "new"


def test_temp_file_keeps_the_same_name_so_duckdb_catalog_name_matches(tmp_path: Path) -> None:
    final = tmp_path / "warehouse.duckdb"

    assert temp_path_for(final).name == final.name
    assert temp_path_for(final) != final


def test_swap_refuses_while_a_write_ahead_log_is_open(tmp_path: Path) -> None:
    final = tmp_path / "warehouse.duckdb"

    with pytest.raises(RuntimeError, match="write-ahead log"), atomic_build(final) as tmp:
        tmp.write_text("new")
        tmp.with_name(f"{tmp.name}.wal").write_text("pending")

    assert not final.exists()
