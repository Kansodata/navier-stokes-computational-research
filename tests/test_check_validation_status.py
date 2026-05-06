from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


def _load_checker_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "check_validation_status.py"
    spec = importlib.util.spec_from_file_location("check_validation_status_module", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module


def test_checker_rejects_failed_status() -> None:
    checker = _load_checker_module()
    with pytest.raises(RuntimeError, match="Fail-closed status"):
        checker._assert_status_not_failed("failed", "unit_test_context")


def test_checker_rejects_unknown_status() -> None:
    checker = _load_checker_module()
    with pytest.raises(RuntimeError, match="Fail-closed status"):
        checker._assert_status_not_failed("unknown", "unit_test_context")


def test_checker_hpc_benchmark_fail_closed_status(tmp_path: Path) -> None:
    checker = _load_checker_module()
    checker.ROOT = tmp_path / "outputs" / "benchmarks"
    artifact_dir = checker.ROOT / "hpc_fftw_benchmark"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "execution_status": "failed",
        "benchmark_status": "failed",
        "scientific_acceptance": "human_review_required",
        "baseline_solver": {"status": "failed"},
        "fftw_solver": {"status": "failed"},
        "comparison": {"consistency_status": "failed", "performance_status": "failed"},
    }
    (artifact_dir / "hpc_fftw_benchmark_summary.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="Fail-closed status"):
        checker._check_hpc_fftw_benchmark()
