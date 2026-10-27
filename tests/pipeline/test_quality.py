import json
from pathlib import Path

from pipeline.quality import build_quality_report, summarize_run_results


def test_summarize_run_results_counts_test_statuses(tmp_path: Path) -> None:
    run_results = tmp_path / "run_results.json"
    run_results.write_text(
        json.dumps(
            {
                "results": [
                    {"unique_id": "test.p.unique_x", "status": "pass", "failures": 0},
                    {"unique_id": "test.p.rel_y", "status": "warn", "failures": 13},
                    {"unique_id": "model.p.fct_orders", "status": "success", "failures": None},
                ]
            }
        )
    )

    summary = summarize_run_results(run_results)

    assert summary.counts == {"pass": 1, "warn": 1}
    assert summary.warnings == [("rel_y", 13)]


def test_report_lists_every_mart_with_row_counts(fixture_warehouse: Path) -> None:
    report = build_quality_report(fixture_warehouse)

    assert report.startswith("# Data quality report")
    assert "| fct_orders |" in report
    assert "| dim_date |" in report
    assert "## dbt tests" in report
