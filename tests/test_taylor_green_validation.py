from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from navier_stokes_research.cli import build_parser
from navier_stokes_research.config import GridConfig
from navier_stokes_research.initial_conditions.factory import create_initial_vorticity
from navier_stokes_research.taylor_green import (
    build_taylor_green_config,
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


def test_taylor_green_cli_flag_available() -> None:
    parser = build_parser()
    args = parser.parse_args(["--taylor-green-validation"])
    assert args.taylor_green_validation is True
