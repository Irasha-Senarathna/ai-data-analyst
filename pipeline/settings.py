"""Pipeline configuration, read from environment variables (see .env.example)."""

import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DBT_DIR = REPO_ROOT / "dbt"


@dataclass(frozen=True)
class PipelineSettings:
    data_dir: Path
    warehouse_path: Path
    kaggle_username: str | None
    kaggle_key: str | None

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"

    @classmethod
    def from_env(cls) -> "PipelineSettings":
        data_dir = Path(os.environ.get("DATA_DIR", REPO_ROOT / "data"))
        warehouse = Path(os.environ.get("WAREHOUSE_PATH", data_dir / "warehouse.duckdb"))
        return cls(
            data_dir=data_dir,
            warehouse_path=warehouse if warehouse.is_absolute() else REPO_ROOT / warehouse,
            kaggle_username=os.environ.get("KAGGLE_USERNAME") or None,
            kaggle_key=os.environ.get("KAGGLE_KEY") or None,
        )
