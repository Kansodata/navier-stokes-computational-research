from __future__ import annotations

import json
from pathlib import Path

import pytest

from navier_stokes_research.cli import build_parser
from navier_stokes_research.convergence import (
    EXTENDED_RESOLUTIONS,
    _relative_difference,
    run_convergence_study,
)


def test_relative_difference_computation() -> None:
    assert _relative_difference(2.0, 2.2) == pytest.approx(0.1)
    assert _relative_difference(0.0, 1e-13) == pytest.approx(0.1)


def test_convergence_study_generates_summary_and_artifacts(tmp_path: Path) -> None:
    result = run_convergence_study(
        base_output_dir=str(tmp_path / "convergence"),
        study_name="test_study",
        resolutions=(16, 24),
        base_resolution=16,
        base_dt=0.0025,
        final_time=0.02,
        viscosity=0.001,
        seed=123,
        save_plots=False,
    )

    summary_path = Path(result["convergence_summary_path"])
    csv_path = Path(result["convergence_metrics_csv_path"])
    plot_path = Path(result["comparison_plot_path"])

    assert summary_path.exists()
    assert csv_path.exists()
    assert plot_path.exists()

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["study_name"] == "test_study"
    assert summary["inputs"]["initial_condition_kind"] == "vortices"
    assert "runs" in summary and len(summary["runs"]) == 2
    assert "relative_differences_consecutive" in summary
    assert "quality_interpretation" in summary
    assert summary["runs"][0]["resolution"] == 16
    assert summary["runs"][1]["resolution"] == 24
    assert summary["runs"][0]["validation_status"] in {"pass", "warn"}


def test_cli_parser_supports_convergence_flag() -> None:
    parser = build_parser()
    args = parser.parse_args(["--convergence-study"])
    assert args.convergence_study is True


def test_cli_parser_supports_convergence_extended_flag() -> None:
    parser = build_parser()
    args = parser.parse_args(["--convergence-study", "--convergence-extended"])
    assert args.convergence_extended is True
    assert EXTENDED_RESOLUTIONS == (32, 64, 128)
