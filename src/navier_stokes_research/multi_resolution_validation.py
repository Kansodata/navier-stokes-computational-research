from __future__ import annotations

import json
import math
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
from navier_stokes_research.validation_schema import build_validation_result

STUDY_NAME = "multi_resolution_energy_enstrophy_2d"
BASE_OUTPUT_DIR = "outputs/benchmarks"
FINAL_TIME = 0.24
BASE_DT = 0.0015
BASE_RESOLUTION = 64
RESOLUTIONS = (32, 64, 96)
VISCOSITY = 0.001
SEED = 2026
RATIO_TOLERANCE_LIMIT = 1.1

SCENARIO_STATUSES = {"passed", "warning", "failed"}


def _build_config(*, resolution: int, dt: float, steps: int, output_dir: Path) -> SimulationConfig:
    return SimulationConfig(
        experiment_name=f"multi_resolution_energy_enstrophy_2d_n{resolution}",
        grid=GridConfig(nx=resolution, ny=resolution, lx=2.0 * np.pi, ly=2.0 * np.pi),
        time=TimeConfig(
            dt=dt,
            steps=steps,
            save_every=max(1, steps // 4),
            cfl_safety=0.8,
            diffusion_safety=0.5,
        ),
        physics=PhysicsConfig(viscosity=VISCOSITY),
        initial_condition=InitialConditionConfig(
            kind="vortices",
            amplitude=1.0,
            smoothing_sigma=6.0,
            seed=SEED,
            vortex_radius=0.35,
            vortex_strength=8.0,
            vortex_distance=1.2,
        ),
        output=OutputConfig(
            output_dir=str(output_dir),
            save_plots=False,
            save_snapshots=False,
            log_level="INFO",
        ),
    )


def _diffusion_margin(config: SimulationConfig) -> float:
    dx = config.grid.lx / config.grid.nx
    dy = config.grid.ly / config.grid.ny
    diffusion_number = config.physics.viscosity * config.time.dt * (2.0 / dx**2 + 2.0 / dy**2)
    return float(config.time.diffusion_safety - diffusion_number)


def _is_finite_scalar(value: Any) -> bool:
    return isinstance(value, (float, int)) and math.isfinite(float(value))


def run_multi_resolution_energy_enstrophy_validation_2d(
    base_output_dir: str = BASE_OUTPUT_DIR,
) -> dict[str, Path]:
    study_dir = Path(base_output_dir) / STUDY_NAME
    study_dir.mkdir(parents=True, exist_ok=True)

    scenarios: list[dict[str, Any]] = []
    warnings: list[str] = []
    unexpected_failures: list[str] = []
    runtime_execution = "passed"

    for resolution in RESOLUTIONS:
        dt = BASE_DT * (BASE_RESOLUTION / resolution)
        steps = max(1, int(round(FINAL_TIME / dt)))
        run_dir = study_dir / f"n{resolution}"
        config = _build_config(resolution=resolution, dt=dt, steps=steps, output_dir=run_dir)

        try:
            run_result = run_simulation(config, validate=True)
        except Exception as exc:  # noqa: BLE001
            runtime_execution = "failed"
            unexpected_failures.append(f"n{resolution}")
            scenarios.append(
                {
                    "resolution": resolution,
                    "dt": float(dt),
                    "steps": int(steps),
                    "final_time": float(steps * dt),
                    "initial_energy": None,
                    "final_energy": None,
                    "initial_enstrophy": None,
                    "final_enstrophy": None,
                    "energy_ratio": None,
                    "enstrophy_ratio": None,
                    "cfl_peak": None,
                    "diffusion_margin": _diffusion_margin(config),
                    "status": "failed",
                    "warnings": [f"unexpected_exception:{type(exc).__name__}"],
                    "resolved_configuration": asdict(config),
                }
            )
            continue

        metrics = run_result.get("metrics")
        validation_report = run_result.get("validation_report")
        if not isinstance(metrics, list) or not metrics or not isinstance(validation_report, dict):
            runtime_execution = "failed"
            unexpected_failures.append(f"n{resolution}")
            scenarios.append(
                {
                    "resolution": resolution,
                    "dt": float(dt),
                    "steps": int(steps),
                    "final_time": float(steps * dt),
                    "initial_energy": None,
                    "final_energy": None,
                    "initial_enstrophy": None,
                    "final_enstrophy": None,
                    "energy_ratio": None,
                    "enstrophy_ratio": None,
                    "cfl_peak": None,
                    "diffusion_margin": _diffusion_margin(config),
                    "status": "failed",
                    "warnings": ["missing_metrics_or_validation_report"],
                    "resolved_configuration": asdict(config),
                }
            )
            continue

        energy = np.array([float(item["energy"]) for item in metrics], dtype=float)
        enstrophy = np.array([float(item["enstrophy"]) for item in metrics], dtype=float)
        cfl = np.array([float(item["cfl"]) for item in metrics], dtype=float)
        finite_ok = bool(np.all(np.isfinite(np.concatenate([energy, enstrophy, cfl]))))

        initial_energy = float(energy[0])
        final_energy = float(energy[-1])
        initial_enstrophy = float(enstrophy[0])
        final_enstrophy = float(enstrophy[-1])
        energy_ratio = float("inf") if initial_energy <= 0.0 else float(final_energy / initial_energy)
        enstrophy_ratio = (
            float("inf") if initial_enstrophy <= 0.0 else float(final_enstrophy / initial_enstrophy)
        )
        cfl_peak = float(np.max(cfl))
        diffusion_margin = _diffusion_margin(config)
        cfl_margin = float(config.time.cfl_safety - cfl_peak)

        scenario_warnings = [str(item) for item in validation_report.get("warnings", [])]
        validation_status = str(validation_report.get("status", "warn"))
        ratio_ok = energy_ratio <= RATIO_TOLERANCE_LIMIT and enstrophy_ratio <= RATIO_TOLERANCE_LIMIT
        safety_ok = cfl_margin > 0.0 and diffusion_margin > 0.0

        if not finite_ok or not safety_ok:
            scenario_status = "failed"
            if not finite_ok:
                scenario_warnings.append("non_finite_metrics_detected")
            if not safety_ok:
                scenario_warnings.append("stability_margin_non_positive")
        elif validation_status == "fail" or not ratio_ok:
            scenario_status = "warning"
            if not ratio_ok:
                scenario_warnings.append("energy_or_enstrophy_ratio_above_limit")
        else:
            scenario_status = "passed"

        if scenario_status == "failed":
            runtime_execution = "failed"
            unexpected_failures.append(f"n{resolution}")

        warnings.extend(f"n{resolution}:{item}" for item in scenario_warnings)
        scenarios.append(
            {
                "resolution": resolution,
                "dt": float(dt),
                "steps": int(steps),
                "final_time": float(steps * dt),
                "initial_energy": initial_energy,
                "final_energy": final_energy,
                "initial_enstrophy": initial_enstrophy,
                "final_enstrophy": final_enstrophy,
                "energy_ratio": energy_ratio,
                "enstrophy_ratio": enstrophy_ratio,
                "cfl_peak": cfl_peak,
                "diffusion_margin": diffusion_margin,
                "status": scenario_status,
                "warnings": scenario_warnings,
                "resolved_configuration": asdict(config),
            }
        )

    status_counts = {key: 0 for key in sorted(SCENARIO_STATUSES)}
    for scenario in scenarios:
        status_counts[scenario["status"]] += 1

    if runtime_execution == "failed":
        overall_status = "failed"
    elif status_counts["warning"] > 0:
        overall_status = "warning"
    else:
        overall_status = "passed"

    normalized = build_validation_result(
        validation_id=STUDY_NAME,
        validation_type="diagnostic",
        status=overall_status,
        claim_scope="numerical_regression_check",
        parameters={
            "resolutions": list(RESOLUTIONS),
            "base_resolution": BASE_RESOLUTION,
            "base_dt": BASE_DT,
            "final_time": FINAL_TIME,
            "viscosity": VISCOSITY,
            "seed": SEED,
        },
        metrics={
            "resolution_count": len(scenarios),
            "status_counts": status_counts,
            "runtime_execution": runtime_execution,
            "energy_enstrophy_regression_status": overall_status,
        },
        thresholds={
            "energy_ratio_upper_bound": RATIO_TOLERANCE_LIMIT,
            "enstrophy_ratio_upper_bound": RATIO_TOLERANCE_LIMIT,
            "cfl_margin_positive": True,
            "diffusion_margin_positive": True,
        },
        artifacts={
            "study_dir": str(study_dir),
            "summary_json": str(
                study_dir / "multi_resolution_energy_enstrophy_summary.json"
            ),
        },
        limitations=[
            "2d_periodic_scope_only",
            "diagnostic_regression_only_not_formal_convergence_proof",
            "not_a_3d_existence_or_smoothness_proof",
        ],
        notes=[
            "This artifact is for controlled multi-resolution regression tracking.",
            "It is not a universal physical-validity statement.",
        ],
    )

    payload = {
        **normalized,
        "study_name": STUDY_NAME,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "domain": "2d_incompressible_periodic",
            "purpose": "multi_resolution_energy_enstrophy_regression",
            "limit": "diagnostic_regression_only_not_formal_convergence_proof",
        },
        "resolutions": scenarios,
        "summary": {
            "resolution_count": len(scenarios),
            "status_counts": status_counts,
            "unexpected_failures": unexpected_failures,
        },
        "acceptance_statuses": {
            "runtime_execution": runtime_execution,
            "energy_enstrophy_regression_status": overall_status,
        },
        "scientific_acceptance": "human_review_required",
        "warnings": warnings,
    }

    summary_path = study_dir / "multi_resolution_energy_enstrophy_summary.json"
    summary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {"output_dir": study_dir, "summary_path": summary_path}
