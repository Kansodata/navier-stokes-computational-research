from __future__ import annotations

import json
from pathlib import Path

from navier_stokes_research.benchmark import run_benchmark
from navier_stokes_research.convergence import run_convergence_study
from navier_stokes_research.reporting import (
    generate_benchmark_report,
    generate_convergence_report,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_generate_benchmark_report_from_minimal_artifacts(tmp_path: Path) -> None:
    root = tmp_path / "bench" / "baseline_2d_incompressible"
    _write(
        root / "benchmark_summary.json",
        json.dumps(
            {
                "config": {"experiment_name": "bench<test>"},
                "final_metrics": {"energy": 1.0, "enstrophy": 2.0, "max_velocity": 3.0, "cfl": 0.1},
                "validation_status": "pass",
                "warnings": ["unsafe <tag>"],
            }
        ),
    )
    _write(root / "validation_report.json", json.dumps({"checks": {"a": {"ok": True}}}))
    _write(root / "benchmark_quality.json", json.dumps({"status": "aprobado", "reasons": [], "recommendation": "ok"}))
    _write(root / "metrics.csv", "step,time,energy,enstrophy,max_velocity,cfl\n0,0,1,1,1,0.1\n")

    report = generate_benchmark_report(root)
    content = report.read_text(encoding="utf-8")
    assert "Reporte de benchmark" in content
    assert "Diagnóstico automático" in content
    assert "&lt;tag&gt;" in content


def test_generate_convergence_report_from_minimal_artifacts(tmp_path: Path) -> None:
    root = tmp_path / "convergence" / "baseline_resolution_study"
    _write(
        root / "convergence_summary.json",
        json.dumps(
            {
                "study_name": "study<1>",
                "created_at_utc": "2026-01-01T00:00:00+00:00",
                "runs": [
                    {
                        "resolution": 16,
                        "validation_status": "pass",
                        "cfl_peak": 0.1,
                        "final_metrics": {"energy": 1.0, "enstrophy": 1.0, "max_velocity": 1.0},
                        "artifacts": {},
                    },
                    {
                        "resolution": 32,
                        "validation_status": "pass",
                        "cfl_peak": 0.1,
                        "final_metrics": {"energy": 1.1, "enstrophy": 1.1, "max_velocity": 1.1},
                        "artifacts": {},
                    },
                ],
                "relative_differences_consecutive": [
                    {"from_resolution": 16, "to_resolution": 32, "energy": 0.1, "enstrophy": 0.1, "max_velocity": 0.1}
                ],
                "estimated_self_convergence_orders": [
                    {
                        "coarse_resolution": 16,
                        "medium_resolution": 32,
                        "fine_resolution": 64,
                        "energy_order": 1.5,
                        "enstrophy_order": 1.25,
                        "max_velocity_order": 0.75,
                        "note": "diagnostic_only_not_formal_proof",
                    }
                ],
                "acceptance_statuses": {
                    "runtime_execution": "passed",
                    "heuristic_consistency": "aprobado",
                    "scientific_acceptance": "human_review_required",
                    "scientific_acceptance_reasons": ["test <reason>"],
                },
                "warnings": ["warn <html>"],
            }
        ),
    )
    _write(root / "convergence_quality.json", json.dumps({"status": "aprobado", "reasons": [], "recommendation": "ok"}))
    _write(root / "convergence_metrics.csv", "resolution,dt\n16,0.01\n")

    report = generate_convergence_report(root)
    content = report.read_text(encoding="utf-8")
    assert "Reporte de estudio de convergencia" in content
    assert "Diagnóstico automático" in content
    assert "Estados de aceptación" in content
    assert "Órdenes estimados de self-convergence" in content
    assert "human_review_required" in content
    assert "diagnostic_only_not_formal_proof" in content
    assert "study&lt;1&gt;" in content
    assert "warn &lt;html&gt;" in content


def test_report_html_exists_after_benchmark_and_convergence_runs(tmp_path: Path) -> None:
    bench_result = run_benchmark(base_output_dir=str(tmp_path / "benchmarks"))
    assert Path(bench_result["benchmark_report_path"]).exists()
    assert Path(bench_result["benchmark_quality_path"]).exists()

    conv_result = run_convergence_study(
        base_output_dir=str(tmp_path / "convergence"),
        study_name="quick",
        resolutions=(16, 24),
        base_resolution=16,
        base_dt=0.0025,
        final_time=0.02,
        viscosity=0.001,
        seed=321,
        save_plots=False,
    )
    assert Path(conv_result["convergence_report_path"]).exists()
    assert Path(conv_result["convergence_quality_path"]).exists()
