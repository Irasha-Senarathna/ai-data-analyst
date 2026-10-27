"""Run dbt against a given DuckDB file.

dbt runs in a subprocess: dbt-duckdb caches its connection in-process, and the
warehouse file must be fully closed before the pipeline swaps it in.
"""

import os
import subprocess  # noqa: S404 - fixed argv, no shell
import sys
from pathlib import Path

from pipeline.settings import DBT_DIR

DBT_EXECUTABLE = Path(sys.executable).parent / "dbt"


class DbtError(RuntimeError):
    """dbt finished with failing models or tests."""


def run_dbt(args: list[str], warehouse_path: Path, *, quiet: bool = True) -> None:
    """Run a dbt command (e.g. ["build"]) and raise DbtError if it fails."""
    command = [
        str(DBT_EXECUTABLE),
        *(["--quiet"] if quiet else []),
        *args,
        "--project-dir",
        str(DBT_DIR),
        "--profiles-dir",
        str(DBT_DIR),
    ]
    env = os.environ | {"DBT_DUCKDB_PATH": str(warehouse_path.resolve())}
    result = subprocess.run(command, env=env, capture_output=quiet, text=True, check=False)  # noqa: S603
    if result.returncode != 0:
        output = (result.stdout or "")[-4000:] if quiet else ""
        raise DbtError(f"dbt {' '.join(args)} failed (exit {result.returncode}).\n{output}")
