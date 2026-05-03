from __future__ import annotations

from pathlib import Path

from navier_stokes_research.interpretation import (
    interpret_benchmark_quality,
    interpret_convergence_quality,
)


def test_benchmark_quality_passes_clean_report(tmp_path: Path) -> None:
    (tmp_path / "benchmark_summary.json").write_text("{}", encoding="utf-8")
    (tmp_path / "validation_report.json").write_text("{}", encoding="utf-8")
    (tmp_path / "metrics.csv").write_text("step,time\n0,0\n", encoding="utf-8")
    summary = {"validation_status": "pass", "warnings": []}
    validation = {
        "checks": {
            "kinetic_energy_trend": {"ratio": 1.0},
            "enstrophy_trend": {"ratio": 1.0},
            "cfl_margin": {"cfl_peak": 0.1, "cfl_limit": 0.8},
        }
    }

    report = interpret_benchmark_quality(
        summary=summary,
        validation_report=validation,
        output_dir=tmp_path,
    )

    assert report["status"] == "aprobado"


def test_benchmark_quality_warns_on_warnings(tmp_path: Path) -> None:
    (tmp_path / "benchmark_summary.json").write_text("{}", encoding="utf-8")
    (tmp_path / "validation_report.json").write_text("{}", encoding="utf-8")
    (tmp_path / "metrics.csv").write_text("step,time\n0,0\n", encoding="utf-8")
    report = interpret_benchmark_quality(
        summary={"validation_status": "pass", "warnings": ["x"]},
        validation_report={"checks": {}},
        output_dir=tmp_path,
    )
    assert report["status"] == "advertencia"
    assert "warnings_presentes" in report["reasons"]


def test_convergence_quality_requires_review_on_high_energy_difference(tmp_path: Path) -> None:
    (tmp_path / "convergence_summary.json").write_text("{}", encoding="utf-8")
    (tmp_path / "convergence_metrics.csv").write_text("resolution\n32\n", encoding="utf-8")
    (tmp_path / "convergence_comparison.png").write_text("fake", encoding="utf-8")
    summary = {
        "runs": [
            {"resolution": 32, "validation_status": "pass", "cfl_peak": 0.1, "config": {"time": {"cfl_safety": 0.8}}},
            {"resolution": 64, "validation_status": "pass", "cfl_peak": 0.1, "config": {"time": {"cfl_safety": 0.8}}},
        ],
        "relative_differences_consecutive": [
            {"energy": 0.9, "enstrophy": 0.1, "max_velocity": 0.05}
        ],
    }

    report = interpret_convergence_quality(summary=summary, output_dir=tmp_path)

    assert report["status"] == "requiere_revision"
    assert "diferencia_relativa_energia_muy_alta" in report["reasons"]
