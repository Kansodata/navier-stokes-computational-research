from __future__ import annotations

import json
from pathlib import Path

from navier_stokes_research.cli import build_parser
from navier_stokes_research.config import (
    ForcingConfig,
    GridConfig,
    InitialConditionConfig,
    OutputConfig,
    PhysicsConfig,
    SimulationConfig,
    TimeConfig,
)
from navier_stokes_research.forcing_validator import run_forced_turbulence_validation_2d
from navier_stokes_research.runner import run_simulation


def test_cli_parser_supports_forced_turbulence_validation_flag() -> None:
    parser = build_parser()
    args = parser.parse_args(["--forced-turbulence-validation-2d"])
    assert args.forced_turbulence_validation_2d is True


def test_runner_records_forcing_budget_metrics_when_forcing_enabled(tmp_path: Path) -> None:
    config = SimulationConfig(
        experiment_name="forcing_metrics_unit",
        grid=GridConfig(nx=24, ny=24),
        time=TimeConfig(dt=0.001, steps=4, save_every=4),
        physics=PhysicsConfig(viscosity=0.001),
        initial_condition=InitialConditionConfig(kind="vortices", seed=10),
        output=OutputConfig(
            output_dir=str(tmp_path / "forcing_metrics_unit"),
            save_plots=False,
            save_snapshots=False,
        ),
        forcing=ForcingConfig(
            enabled=True,
            forcing_type="fourier_deterministic_narrow_band",
            k_min=2.0,
            k_max=4.0,
            seed=10,
            target_energy_input_rate=0.004,
            ekman_drag=0.05,
        ),
    )
    result = run_simulation(config, validate=True)
    forcing_metrics = result["forcing_metrics"]
    assert isinstance(forcing_metrics, list)
    assert len(forcing_metrics) == config.time.steps + 1
    assert Path(result["forcing_metrics_csv"]).exists()
    for row in forcing_metrics:
        assert "epsilon_in" in row
        assert "epsilon_viscous" in row
        assert "epsilon_drag" in row
        assert "energy_balance_residual_normalized" in row


def test_forced_turbulence_validation_summary_schema(tmp_path: Path) -> None:
    result = run_forced_turbulence_validation_2d(base_output_dir=str(tmp_path / "benchmarks"))
    summary_path = Path(result["summary_path"])
    assert summary_path.exists()
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0"
    assert payload["validation_id"] == "forced_turbulence_validation_2d"
    assert payload["validation_type"] == "diagnostic"
    assert payload["scientific_acceptance"] == "human_review_required"
    assert payload["acceptance_statuses"]["runtime_execution"] == "passed"
    assert payload["acceptance_statuses"]["accuracy_status"] in {"passed", "warning", "failed"}
    assert payload["acceptance_statuses"]["budget_status"] in {"passed", "warning", "failed"}
    assert "epsilon_in_mean" in payload["budget_summary"]
    assert "slope_fits" in payload["spectral_summary"]
    assert payload["summary"]["unexpected_failures"] == []
