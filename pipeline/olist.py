"""Olist Brazilian E-Commerce dataset (Kaggle, CC BY-NC-SA 4.0)."""

import zipfile
from pathlib import Path

import httpx

from pipeline.download import DownloadResult, download_file

OLIST_URL = "https://www.kaggle.com/api/v1/datasets/download/olistbr/brazilian-ecommerce"

# raw table name (raw.olist_<name>) -> file inside the Kaggle zip
OLIST_TABLES: dict[str, str] = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


def kaggle_auth(username: str | None, key: str | None) -> tuple[str, str] | None:
    """Basic auth for Kaggle when a token is configured; public datasets work without one."""
    if username and key:
        return (username, key)
    return None


def download_olist(
    client: httpx.Client, raw_dir: Path, auth: tuple[str, str] | None = None
) -> DownloadResult:
    return download_file(client, OLIST_URL, raw_dir / "olist" / "olist.zip", auth=auth)


def extract_olist(zip_path: Path, out_dir: Path) -> dict[str, Path]:
    """Extract only the expected CSVs (by exact name, so no path traversal)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    with zipfile.ZipFile(zip_path) as archive:
        members = set(archive.namelist())
        for table, filename in OLIST_TABLES.items():
            if filename not in members:
                raise FileNotFoundError(f"{filename} is missing from {zip_path}")
            target = out_dir / filename
            target.write_bytes(archive.read(filename))
            paths[table] = target
    return paths
