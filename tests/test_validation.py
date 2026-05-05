from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from navier_stokes_research.config import (
    GridConfig,
    InitialConditionConfig,
    OutputConfig,
    PhysicsConfig,
    SimulationConfig,
    TimeConfig,
)
from navier_stokes_research.runner import run_simulation
from navier_stokes_research.solver.numerics import assert_finite
from navier_stokes_research.validation import evaluate_validation, load_metrics_csv, write_validation_report


def _small_config(output_dir: Path) -> SimulationConfig:
    return SimulationConfig(
        experiment_name="test_validation",
        grid=GridConfig(nx=24, ny=24),
        time=TimeConfig(dt=0.002, steps=30, save_every=15, cfl_safety=0.8, diffusion_safety=0.5),
        physics=PhysicsConfig(viscosity=0.001),
        initial_condition=InitialConditionConfig(kind="random", seed=99, smoothing_sigma=5.0),
        output=OutputConfig(
            output_dir=str(output_dir),
            save_plots=False,
            save_snapshots=False,
            log_level="INFO",
        ),
    )


def test_validation_output_schema(tmp_path: Path) -> None:
    config = _small_config(tmp_path / "run_schema")
    result = run_simulation(config, validate=True)

    report = result["validation_report"]
    assert isinstance(report, dict)
    assert report["status"] in {"pass", "warn"}
    assert "warnings" in report and isinstance(report["warnings"], list)
    assert "checks" in report and isinstance(report["checks"], dict)
    assert "final_metrics" in report and isinstance(report["final_metrics"], dict)

    report_path = result["validation_report_path"]
    loaded = json.loads(Path(report_path).read_text(encoding="utf-8"))
    assert loaded["status"] == report["status"]


def test_deterministic_metrics_under_fixed_seed(tmp_path: Path) -> None:
    config_a = _small_config(tmp_path / "run_a")
    config_b = _small_config(tmp_path / "run_b")

    result_a = run_simulation(config_a, validate=True)
    result_b = run_simulation(config_b, validate=True)

    metrics_a = load_metrics_csv(result_a["metrics_csv"])
    metrics_b = load_metrics_csv(result_b["metrics_csv"])
    assert len(metrics_a) == len(metrics_b)

    final_a = metrics_a[-1]
    final_b = metrics_b[-1]
    assert final_a["energy"] == pytest.approx(final_b["energy"], rel=1e-12, abs=1e-12)
    assert final_a["enstrophy"] == pytest.approx(final_b["enstrophy"], rel=1e-12, abs=1e-12)
    assert final_a["max_velocity"] == pytest.approx(final_b["max_velocity"], rel=1e-12, abs=1e-12)
    assert final_a["cfl"] == pytest.approx(final_b["cfl"], rel=1e-12, abs=1e-12)


def test_validation_warns_on_non_finite_metrics() -> None:
    fake_metrics = [
        {"step": 0.0, "time": 0.0, "energy": 1.0, "enstrophy": 1.0, "max_velocity": 1.0, "cfl": 0.1},
        {"step": 1.0, "time": 1.0, "energy": np.nan, "enstrophy": 1.0, "max_velocity": 1.0, "cfl": 0.1},
    ]
    config = SimulationConfig(
        experiment_name="fake",
        grid=GridConfig(),
        time=TimeConfig(),
        physics=PhysicsConfig(),
        initial_condition=InitialConditionConfig(),
        output=OutputConfig(),
    )
    report = evaluate_validation(fake_metrics, config)
    assert report["status"] == "warn"
    assert "non_finite_metrics_detected" in report["warnings"]


def test_validation_report_serializes_high_velocity_growth_check(tmp_path: Path) -> None:
    fake_metrics = [
        {"step": 0.0, "time": 0.0, "energy": 1.0, "enstrophy": 1.0, "max_velocity": 0.75, "cfl": 0.1},
        {"step": 1.0, "time": 1.0, "energy": 0.99, "enstrophy": 0.98, "max_velocity": 0.76, "cfl": 0.1},
    ]
    config = SimulationConfig(
        experiment_name="json_safe_validation",
        grid=GridConfig(),
        time=TimeConfig(),
        physics=PhysicsConfig(),
        initial_condition=InitialConditionConfig(),
        output=OutputConfig(),
    )

    report = evaluate_validation(fake_metrics, config)
    assert isinstance(report["checks"]["max_velocity_growth"]["ok"], bool)

    report_path = tmp_path / "validation_report.json"
    write_validation_report(report_path, report)
    loaded = json.loads(report_path.read_text(encoding="utf-8"))
    assert loaded["checks"]["max_velocity_growth"]["ok"] is True


def test_assert_finite_fails_on_nan() -> None:
    with pytest.raises(FloatingPointError):
        assert_finite("bad", np.array([1.0, np.nan]))
