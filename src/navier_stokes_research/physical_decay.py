from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from navier_stokes_research.config import (
    GridConfig,
    InitialConditionConfig,
    OutputConfig,
    PhysicsConfig,
    SimulationConfig,
    TimeConfig,
)
from navier_stokes_research.runner import run_simulation

DECAY_RELATIVE_TOLERANCE = 1e-10


def _non_increasing_with_tolerance(
    initial_value: float,
    final_value: float,
    relative_tolerance: float = DECAY_RELATIVE_TOLERANCE,
) -> bool:
    if not np.isfinite(initial_value) or not np.isfinite(final_value):
        return False
    tolerance = relative_tolerance * max(abs(initial_value), 1.0)
    return final_value <= initial_value + tolerance


def _diffusion_margin(config: SimulationConfig) -> float:
    dx = config.grid.lx / config.grid.nx
    dy = config.grid.ly / config.grid.ny
    diffusion_number = config.physics.viscosity * config.time.dt * (2.0 / dx**2 + 2.0 / dy**2)
    return float(config.time.diffusion_safety - diffusion_number)


def _build_physical_decay_config(base_output_dir: str) -> SimulationConfig:
    output_dir = f"{base_output_dir}/physical_decay_2d"
    return SimulationConfig(
        experiment_name="physical_decay_validation_2d_unforced",
        grid=GridConfig(nx=64, ny=64, lx=2.0 * np.pi, ly=2.0 * np.pi),
        time=TimeConfig(
            dt=0.0015,
            steps=160,
            save_every=40,
            cfl_safety=0.8,
            diffusion_safety=0.5,
        ),
        physics=PhysicsConfig(viscosity=0.001),
        initial_condition=InitialConditionConfig(
            kind="vortices",
            amplitude=1.0,
            seed=2026,
            vortex_radius=0.35,
            vortex_strength=8.0,
            vortex_distance=1.2,
        ),
        output=OutputConfig(
            output_dir=output_dir,
            save_plots=False,
            save_snapshots=False,
            log_level="INFO",
        ),
    )


def run_physical_decay_validation(base_output_dir: str = "outputs/benchmarks") -> dict[str, Path]:
    config = _build_physical_decay_config(base_output_dir)
    run_result = run_simulation(config, validate=True)

    metrics = run_result.get("metrics")
    if not isinstance(metrics, list) or not metrics:
        raise RuntimeError("Metrics are missing; cannot perform physical decay validation.")
    validation_report = run_result.get("validation_report")
    if not isinstance(validation_report, dict):
        raise RuntimeError("Validation report is missing; cannot evaluate runtime execution status.")

    energy_series = np.array([float(item["energy"]) for item in metrics], dtype=float)
    enstrophy_series = np.array([float(item["enstrophy"]) for item in metrics], dtype=float)
    max_velocity_series = np.array([float(item["max_velocity"]) for item in metrics], dtype=float)
    cfl_series = np.array([float(item["cfl"]) for item in metrics], dtype=float)

    flat_values = np.concatenate([energy_series, enstrophy_series, max_velocity_series, cfl_series])
    finite_metrics_ok = bool(np.all(np.isfinite(flat_values)))
    viscosity_ok = bool(config.physics.viscosity > 0.0)
    initial_energy_ok = bool(energy_series[0] > 0.0) if finite_metrics_ok else False
    initial_enstrophy_ok = bool(enstrophy_series[0] > 0.0) if finite_metrics_ok else False
    energy_decay_ok = _non_increasing_with_tolerance(float(energy_series[0]), float(energy_series[-1]))
    enstrophy_decay_ok = _non_increasing_with_tolerance(float(enstrophy_series[0]), float(enstrophy_series[-1]))
    cfl_peak = float(np.max(cfl_series))
    cfl_margin = float(config.time.cfl_safety - cfl_peak)
    cfl_margin_ok = bool(cfl_margin > 0.0)
    diffusion_margin = _diffusion_margin(config)
    diffusion_margin_ok = bool(diffusion_margin > 0.0)

    checks: dict[str, dict[str, Any]] = {
        "finite_metrics": {
            "ok": finite_metrics_ok,
            "details": "All recorded energy, enstrophy, max_velocity, and cfl values are finite.",
        },
        "positive_viscosity": {
            "ok": viscosity_ok,
            "value": float(config.physics.viscosity),
        },
        "positive_initial_energy": {
            "ok": initial_energy_ok,
            "value": float(energy_series[0]),
        },
        "positive_initial_enstrophy": {
            "ok": initial_enstrophy_ok,
            "value": float(enstrophy_series[0]),
        },
        "energy_non_increasing": {
            "ok": energy_decay_ok,
            "start": float(energy_series[0]),
            "end": float(energy_series[-1]),
            "relative_tolerance": DECAY_RELATIVE_TOLERANCE,
        },
        "enstrophy_non_increasing": {
            "ok": enstrophy_decay_ok,
            "start": float(enstrophy_series[0]),
            "end": float(enstrophy_series[-1]),
            "relative_tolerance": DECAY_RELATIVE_TOLERANCE,
        },
        "cfl_margin_positive": {
            "ok": cfl_margin_ok,
            "cfl_peak": cfl_peak,
            "cfl_limit": float(config.time.cfl_safety),
            "margin": cfl_margin,
        },
        "diffusion_margin_positive": {
            "ok": diffusion_margin_ok,
            "margin": diffusion_margin,
            "diffusion_limit": float(config.time.diffusion_safety),
        },
    }

    critical_failed = [name for name, payload in checks.items() if not bool(payload["ok"])]
    warnings: list[str] = []
    warnings.extend(str(item) for item in validation_report.get("warnings", []))
    if critical_failed:
        warnings.append("physical_decay_critical_checks_failed")

    runtime_status = "passed"
    validation_status = str(validation_report.get("status", "warn"))
    if validation_status == "pass":
        runtime_status = "passed"
    elif validation_status == "warn":
        runtime_status = "warning"
    else:
        runtime_status = "failed"

    if critical_failed:
        physical_decay_status = "failed"
    elif warnings:
        physical_decay_status = "warning"
    else:
        physical_decay_status = "passed"

    output_dir = Path(config.output.output_dir)
    json_path = output_dir / "physical_decay_validation.json"
    payload = {
        "study_name": "physical_decay_2d",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "resolved_configuration": asdict(config),
        "checks": checks,
        "metrics_summary": {
            "samples": len(metrics),
            "initial_energy": float(energy_series[0]),
            "final_energy": float(energy_series[-1]),
            "initial_enstrophy": float(enstrophy_series[0]),
            "final_enstrophy": float(enstrophy_series[-1]),
            "cfl_peak": cfl_peak,
        },
        "acceptance_statuses": {
            "runtime_execution": runtime_status,
            "physical_decay_status": physical_decay_status,
            "scientific_acceptance": "human_review_required",
            "scientific_acceptance_reasons": [
                "controlled_2d_unforced_viscous_case_only",
                "not_a_3d_existence_or_smoothness_proof",
                "decay_checks_are_numerical_diagnostics_not_formal_proof",
            ],
        },
        "warnings": warnings,
        "artifacts": {
            "output_dir": str(output_dir),
            "metrics_csv": str(run_result["metrics_csv"]),
            "validation_report_path": str(run_result["validation_report_path"]),
            "resolved_config_path": str(output_dir / "resolved_config.json"),
        },
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {
        "output_dir": output_dir,
        "physical_decay_validation_path": json_path,
        "metrics_csv_path": Path(run_result["metrics_csv"]),
        "validation_report_path": Path(run_result["validation_report_path"]),
    }
