import zipfile
from pathlib import Path

import pytest

from pipeline.olist import OLIST_TABLES, extract_olist, kaggle_auth


def write_zip(path: Path, members: dict[str, str]) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in members.items():
            archive.writestr(name, content)
    return path


def all_members() -> dict[str, str]:
    return {filename: "col\nvalue\n" for filename in OLIST_TABLES.values()}


def test_there_are_nine_olist_tables() -> None:
    assert len(OLIST_TABLES) == 9


def test_extract_returns_a_csv_path_per_table(tmp_path: Path) -> None:
    zip_path = write_zip(tmp_path / "olist.zip", all_members())

    paths = extract_olist(zip_path, tmp_path / "csv")

    assert set(paths) == set(OLIST_TABLES)
    assert all(path.is_file() for path in paths.values())


def test_extract_ignores_unexpected_and_path_traversal_members(tmp_path: Path) -> None:
    members = all_members() | {"../evil.csv": "x", "notes.txt": "x"}
    zip_path = write_zip(tmp_path / "olist.zip", members)

    extract_olist(zip_path, tmp_path / "csv")

    assert not (tmp_path / "evil.csv").exists()
    assert not (tmp_path / "csv" / "notes.txt").exists()


def test_extract_fails_when_a_table_is_missing(tmp_path: Path) -> None:
    members = all_members()
    members.pop("olist_orders_dataset.csv")
    zip_path = write_zip(tmp_path / "olist.zip", members)

    with pytest.raises(FileNotFoundError, match="olist_orders_dataset.csv"):
        extract_olist(zip_path, tmp_path / "csv")


def test_kaggle_auth_is_none_without_credentials() -> None:
    assert kaggle_auth(None, None) is None
    assert kaggle_auth("user", "") is None


def test_kaggle_auth_uses_credentials_when_set() -> None:
    assert kaggle_auth("user", "key") == ("user", "key")
