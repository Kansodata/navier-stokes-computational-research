from __future__ import annotations

import json
from pathlib import Path

from navier_stokes_research.cli import build_parser
from navier_stokes_research.hpc_benchmark import run_hpc_fftw_benchmark


def test_cli_parser_supports_hpc_fftw_benchmark_flag() -> None:
    parser = build_parser()
    args = parser.parse_args(["--hpc-fftw-benchmark"])
    assert args.hpc_fftw_benchmark is True


def test_hpc_benchmark_generates_expected_json_schema(tmp_path: Path, monkeypatch) -> None:
    from navier_stokes_research import hpc_benchmark as benchmark

    def fake_baseline_metrics(**_: object) -> dict[str, object]:
        return {
            "solver_name": "baseline_numpy_fft",
            "resolution": 512,
            "steps": 2,
            "dt": 1.0e-4,
            "final_time": 2.0e-4,
            "initialization_time_seconds": 0.1,
            "total_runtime_seconds": 0.4,
            "average_step_time_seconds": 0.2,
            "final_energy": 1.0,
            "final_enstrophy": 2.0,
            "max_cfl": 0.2,
            "status": "passed",
            "warnings": [],
        }

    def fake_fftw_metrics(**_: object) -> dict[str, object]:
        return {
            "solver_name": "fftw_opt_in_solver512",
            "resolution": 512,
            "steps": 2,
            "dt": 1.0e-4,
            "final_time": 2.0e-4,
            "initialization_time_seconds": 0.2,
            "total_runtime_seconds": 0.2,
            "average_step_time_seconds": 0.1,
            "final_energy": 1.001,
            "final_enstrophy": 2.002,
            "max_cfl": 0.21,
            "status": "passed",
            "warnings": [],
            "fftw_effort": "FFTW_MEASURE",
            "threads": 4,
        }

    monkeypatch.setattr(benchmark, "_baseline_metrics", fake_baseline_metrics)
    monkeypatch.setattr(benchmark, "_fftw_metrics", fake_fftw_metrics)

    result = run_hpc_fftw_benchmark(base_output_dir=str(tmp_path / "benchmarks"))
    summary_path = Path(result["summary_path"])
    assert summary_path.exists()
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "benchmark_name",
        "created_at_utc",
        "scientific_scope",
        "scientific_acceptance",
        "execution_status",
        "benchmark_status",
        "warnings",
        "baseline_solver",
        "fftw_solver",
        "comparison",
        "environment",
        "parameters",
        "rollback_note",
    }
    assert required.issubset(payload.keys())
    assert payload["scientific_acceptance"] == "human_review_required"
    assert "3d" not in payload["scientific_scope"].lower()
    assert payload["comparison"]["speedup_ratio"] == 2.0
    assert payload["execution_status"] == "passed"
    assert payload["benchmark_status"] in {"passed", "warning"}


def test_hpc_benchmark_fail_closed_when_solver_fails(tmp_path: Path, monkeypatch) -> None:
    from navier_stokes_research import hpc_benchmark as benchmark

    def fake_baseline_metrics(**_: object) -> dict[str, object]:
        return {
            "solver_name": "baseline_numpy_fft",
            "resolution": 512,
            "steps": 2,
            "dt": 1.0e-4,
            "final_time": 2.0e-4,
            "initialization_time_seconds": 0.1,
            "total_runtime_seconds": 0.4,
            "average_step_time_seconds": 0.2,
            "final_energy": 1.0,
            "final_enstrophy": 2.0,
            "max_cfl": 0.2,
            "status": "failed",
            "warnings": ["runtime_exception:FloatingPointError"],
        }

    def fake_fftw_metrics(**_: object) -> dict[str, object]:
        return {
            "solver_name": "fftw_opt_in_solver512",
            "resolution": 512,
            "steps": 2,
            "dt": 1.0e-4,
            "final_time": 2.0e-4,
            "initialization_time_seconds": 0.2,
            "total_runtime_seconds": 0.2,
            "average_step_time_seconds": 0.1,
            "final_energy": 1.0,
            "final_enstrophy": 2.0,
            "max_cfl": 0.2,
            "status": "passed",
            "warnings": [],
        }

    monkeypatch.setattr(benchmark, "_baseline_metrics", fake_baseline_metrics)
    monkeypatch.setattr(benchmark, "_fftw_metrics", fake_fftw_metrics)
    result = run_hpc_fftw_benchmark(base_output_dir=str(tmp_path / "benchmarks"))
    payload = json.loads(Path(result["summary_path"]).read_text(encoding="utf-8"))
    assert payload["execution_status"] == "failed"
    assert payload["benchmark_status"] == "failed"
