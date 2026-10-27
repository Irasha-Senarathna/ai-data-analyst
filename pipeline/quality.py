"""Data-quality report: mart row counts, null rates and dbt test results.

`python -m pipeline.quality` writes docs/data_quality.md from the current
warehouse and the last dbt run (dbt/target/run_results.json).
"""

import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import duckdb

from pipeline.settings import DBT_DIR, REPO_ROOT, PipelineSettings

RUN_RESULTS = DBT_DIR / "target" / "run_results.json"
REPORT_PATH = REPO_ROOT / "docs" / "data_quality.md"
MARTS_SCHEMA = "marts"


@dataclass(frozen=True)
class TestSummary:
    counts: dict[str, int]
    warnings: list[tuple[str, int]]
    failures: list[tuple[str, int]]


def summarize_run_results(path: Path) -> TestSummary:
    results = json.loads(path.read_text())["results"]
    tests = [result for result in results if result["unique_id"].startswith("test.")]
    counts = Counter(result["status"] for result in tests)

    def named(status: str) -> list[tuple[str, int]]:
        return [
            (result["unique_id"].split(".")[2], int(result["failures"] or 0))
            for result in tests
            if result["status"] == status
        ]

    return TestSummary(dict(counts), named("warn"), named("fail") + named("error"))


def mart_tables(con: duckdb.DuckDBPyConnection) -> list[str]:
    rows = con.execute(
        "select table_name from information_schema.tables where table_schema = ? order by 1",
        [MARTS_SCHEMA],
    ).fetchall()
    return [str(row[0]) for row in rows]


def null_rates(con: duckdb.DuckDBPyConnection, table: str) -> list[tuple[str, float]]:
    """Columns with any nulls, and the share of rows that are null."""
    summary = con.execute(f"summarize {MARTS_SCHEMA}.{table}").fetchall()  # noqa: S608
    rates = [(str(row[0]), float(row[-1])) for row in summary]  # last column = null_percentage
    return [(column, rate) for column, rate in rates if rate > 0]


def row_count(con: duckdb.DuckDBPyConnection, table: str) -> int:
    row = con.execute(f"select count(*) from {MARTS_SCHEMA}.{table}").fetchone()  # noqa: S608
    return int(row[0]) if row else 0


def build_quality_report(warehouse_path: Path, run_results: Path = RUN_RESULTS) -> str:
    lines = ["# Data quality report", "", f"Warehouse: `{warehouse_path.name}`", ""]
    lines += ["## Marts", "", "| Table | Rows | Columns with nulls (% null) |", "|---|---:|---|"]
    with duckdb.connect(str(warehouse_path), read_only=True) as con:
        for table in mart_tables(con):
            nulls = ", ".join(f"{col} ({rate:.1f}%)" for col, rate in null_rates(con, table))
            lines.append(f"| {table} | {row_count(con, table):,} | {nulls or '—'} |")

    lines += ["", "## dbt tests", ""]
    if not run_results.is_file():
        lines.append("No dbt run results found. Run `make pipeline` first.")
        return "\n".join(lines) + "\n"
    summary = summarize_run_results(run_results)
    lines.append(", ".join(f"{status}: {n}" for status, n in sorted(summary.counts.items())))
    for title, items in (("Warnings", summary.warnings), ("Failures", summary.failures)):
        if items:
            lines += ["", f"### {title}", "", "| Test | Rows |", "|---|---:|"]
            lines += [f"| `{name}` | {rows:,} |" for name, rows in items]
    return "\n".join(lines) + "\n"


def main() -> int:
    settings = PipelineSettings.from_env()
    REPORT_PATH.write_text(build_quality_report(settings.warehouse_path))
    print(f"Wrote {REPORT_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
