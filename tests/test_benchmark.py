from __future__ import annotations

import json
from pathlib import Path

from navier_stokes_research.benchmark import run_benchmark


def test_benchmark_run_produces_summary(tmp_path: Path) -> None:
    result = run_benchmark(base_output_dir=str(tmp_path / "benchmarks"))
    summary_path = Path(result["benchmark_summary_path"])
    validation_path = Path(result["validation_report_path"])
    metrics_path = Path(result["metrics_csv"])
    quality_path = Path(result["benchmark_quality_path"])

    assert summary_path.exists()
    assert validation_path.exists()
    assert metrics_path.exists()
    assert quality_path.exists()

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["validation_status"] in {"pass", "warn"}
    assert "final_metrics" in summary
    assert "warnings" in summary
