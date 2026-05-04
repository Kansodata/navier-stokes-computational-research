from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from navier_stokes_research.cli import build_parser
from navier_stokes_research.config import GridConfig
from navier_stokes_research.initial_conditions.factory import create_initial_vorticity
from navier_stokes_research.taylor_green import (
    _safe_error_convergence_order,
    build_taylor_green_config,
    run_taylor_green_convergence_study,
    run_taylor_green_validation,
    taylor_green_velocity_exact,
)


def test_exact_solution_matches_initial_condition_at_t0() -> None:
    grid = GridConfig(nx=32, ny=32, lx=2.0 * np.pi, ly=2.0 * np.pi)
    u0, v0 = taylor_green_velocity_exact(grid=grid, viscosity=0.001, time_value=0.0)

    x = np.linspace(0.0, grid.lx, grid.nx, endpoint=False)
    y = np.linspace(0.0, grid.ly, grid.ny, endpoint=False)
    xx, yy = np.meshgrid(x, y, indexing="ij")
    expected_u = np.sin(xx) * np.cos(yy)
    expected_v = -np.cos(xx) * np.sin(yy)

    assert np.allclose(u0, expected_u)
    assert np.allclose(v0, expected_v)


def test_taylor_green_initial_vorticity_field() -> None:
    grid = GridConfig(nx=16, ny=16, lx=2.0 * np.pi, ly=2.0 * np.pi)
    config = build_taylor_green_config(resolution=16).initial_condition
    vorticity = create_initial_vorticity(config, grid)
    assert np.all(np.isfinite(vorticity))
    assert vorticity.shape == (16, 16)


def test_taylor_green_validation_writes_expected_json(tmp_path: Path) -> None:
    result = run_taylor_green_validation(base_output_dir=str(tmp_path / "benchmarks"))
    report_path = Path(result["report_path"])
    assert report_path.exists()

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["status"] in {"passed", "failed"}
    assert payload["execution_status"] in {"passed", "failed"}
    assert payload["accuracy_status"] in {"passed", "failed", "warning", "not_evaluated"}
    assert isinstance(payload["warnings"], list)
    assert payload["status"] == payload["execution_status"]
    assert "errors" in payload
    assert "l2" in payload["errors"]
    assert "linf" in payload["errors"]
    assert np.isfinite(payload["errors"]["l2"])
    assert np.isfinite(payload["errors"]["linf"])



def test_safe_error_convergence_order() -> None:
    assert _safe_error_convergence_order(0.25, 0.0625, 2.0) == np.float64(2.0)
    assert _safe_error_convergence_order(0.25, 0.5, 2.0) < 0.0
    assert _safe_error_convergence_order(None, 0.5, 2.0) is None
    assert _safe_error_convergence_order(1e-15, 1e-15, 2.0) is None


def test_taylor_green_convergence_study_writes_summary_and_csv(tmp_path: Path) -> None:
    result = run_taylor_green_convergence_study(
        base_output_dir=str(tmp_path / "benchmarks"),
        study_name="tg_convergence_test",
        resolutions=(16, 32, 64),
        base_resolution=16,
        base_dt=0.001,
        final_time=0.002,
        viscosity=0.001,
    )

    summary_path = Path(result["summary_path"])
    csv_path = Path(result["metrics_csv_path"])
    assert summary_path.exists()
    assert csv_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["study_name"] == "tg_convergence_test"
    assert payload["inputs"]["resolutions"] == [16, 32, 64]
    assert len(payload["runs"]) == 3
    assert len(payload["orders"]) == 2
    assert payload["acceptance_statuses"]["scientific_acceptance"] == "human_review_required"
    assert payload["acceptance_statuses"]["formal_error_convergence"] in {
        "passed_roundoff_floor",
        "human_review_required",
    }

def test_taylor_green_cli_flag_available() -> None:
    parser = build_parser()
    args = parser.parse_args(["--taylor-green-validation"])
    assert args.taylor_green_validation is True


def test_taylor_green_convergence_cli_flag_available() -> None:
    parser = build_parser()
    args = parser.parse_args(["--taylor-green-convergence"])
    assert args.taylor_green_convergence is True
