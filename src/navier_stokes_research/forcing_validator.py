from __future__ import annotations

import json
import math
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from navier_stokes_research.config import (
    ForcingConfig,
    GridConfig,
    InitialConditionConfig,
    OutputConfig,
    PhysicsConfig,
    SimulationConfig,
    TimeConfig,
)
from navier_stokes_research.runner import run_simulation
from navier_stokes_research.solver import NavierStokesSpectralSolver
from navier_stokes_research.spectral_diagnostics import compute_velocity_energy_spectrum_2d
from navier_stokes_research.validation_schema import build_validation_result

STUDY_NAME = "forced_turbulence_validation_2d"
ENERGY_BALANCE_RESIDUAL_LIMIT = 2.5
TRANSIENT_FRACTION = 0.5
STATIONARITY_RELATIVE_SPREAD_LIMIT = 0.35
MIN_SLOPE_FIT_POINTS = 3


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite_values(values: list[float]) -> bool:
    return bool(values) and all(math.isfinite(float(value)) for value in values)


def _window(values: list[dict[str, float]], transient_fraction: float = TRANSIENT_FRACTION) -> list[dict[str, float]]:
    if not values:
        return []
    start = min(len(values) - 1, max(0, int(math.floor(len(values) * transient_fraction))))
    return values[start:]


def _mean(values: list[float]) -> float:
    return float(np.mean(np.asarray(values, dtype=float)))


def _relative_spread(values: list[float]) -> float:
    array = np.asarray(values, dtype=float)
    denominator = max(abs(float(np.mean(array))), 1.0e-14)
    return float((float(np.max(array)) - float(np.min(array))) / denominator)


def _fit_slope(
    radial_wavenumbers: list[float],
    radial_energy: list[float],
    *,
    k_min: float,
    k_max: float,
    label: str,
) -> dict[str, Any]:
    k = np.asarray(radial_wavenumbers, dtype=float)
    energy = np.asarray(radial_energy, dtype=float)
    mask = (k >= k_min) & (k <= k_max) & (k > 0.0) & (energy > 0.0)
    warnings: list[str] = []
    if int(np.count_nonzero(mask)) < MIN_SLOPE_FIT_POINTS:
        return {
            "label": label,
            "status": "warning",
            "slope": None,
            "fit_points": int(np.count_nonzero(mask)),
            "warnings": ["insufficient_inertial_range_for_slope_fit"],
        }
    x = np.log(k[mask])
    y = np.log(energy[mask])
    slope, intercept = np.polyfit(x, y, deg=1)
    predicted = slope * x + intercept
    rmse = float(np.sqrt(np.mean((y - predicted) ** 2)))
    if rmse > 1.0:
        warnings.append("large_log_spectrum_fit_residual")
    return {
        "label": label,
        "status": "warning" if warnings else "diagnostic_only",
        "slope": float(slope),
        "fit_points": int(np.count_nonzero(mask)),
        "rmse_log": rmse,
        "fit_range": {"k_min": float(k_min), "k_max": float(k_max)},
        "warnings": warnings,
    }


def _build_forced_config(base_output_dir: str) -> SimulationConfig:
    output_dir = str(Path(base_output_dir) / STUDY_NAME)
    return SimulationConfig(
        experiment_name=STUDY_NAME,
        grid=GridConfig(nx=48, ny=48),
        time=TimeConfig(dt=0.0015, steps=180, save_every=45, cfl_safety=0.8, diffusion_safety=0.5),
        physics=PhysicsConfig(viscosity=0.0015),
        initial_condition=InitialConditionConfig(
            kind="vortices",
            amplitude=0.8,
            smoothing_sigma=6.0,
            seed=2026,
            vortex_radius=0.35,
            vortex_strength=6.0,
            vortex_distance=1.2,
        ),
        output=OutputConfig(
            output_dir=output_dir,
            save_plots=False,
            save_snapshots=True,
            log_level="INFO",
        ),
        forcing=ForcingConfig(
            enabled=True,
            forcing_type="fourier_deterministic_narrow_band",
            k_min=2.0,
            k_max=4.0,
            seed=2026,
            target_energy_input_rate=0.02,
            ekman_drag=0.002,
        ),
    )


def run_forced_turbulence_validation_2d(
    base_output_dir: str = "outputs/benchmarks",
) -> dict[str, Path]:
    config = _build_forced_config(base_output_dir)
    output_dir = Path(config.output.output_dir)
    warnings: list[str] = []
    unexpected_failures: list[str] = []
    runtime_execution = "passed"

    try:
        run_result = run_simulation(config, validate=True)
    except Exception as exc:  # noqa: BLE001
        runtime_execution = "failed"
        unexpected_failures.append(f"runtime_exception:{type(exc).__name__}")
        run_result = {}

    forcing_metrics = run_result.get("forcing_metrics", [])
    if not isinstance(forcing_metrics, list):
        forcing_metrics = []
    averaging_window = _window(forcing_metrics)

    budget_status = "failed"
    budget_summary: dict[str, Any] = {
        "window_start_index": len(forcing_metrics) - len(averaging_window),
        "samples": len(averaging_window),
        "residual_limit": ENERGY_BALANCE_RESIDUAL_LIMIT,
    }
    if averaging_window:
        eps_in = [float(row["epsilon_in"]) for row in averaging_window]
        eps_viscous = [float(row["epsilon_viscous"]) for row in averaging_window]
        eps_drag = [float(row["epsilon_drag"]) for row in averaging_window]
        residuals = [float(row["energy_balance_residual_normalized"]) for row in averaging_window]
        finite_budget = _finite_values(eps_in + eps_viscous + eps_drag + residuals)
        mean_residual = _mean(residuals) if finite_budget else float("inf")
        budget_summary.update(
            {
                "epsilon_in_mean": _mean(eps_in) if finite_budget else None,
                "epsilon_viscous_mean": _mean(eps_viscous) if finite_budget else None,
                "epsilon_drag_mean": _mean(eps_drag) if finite_budget else None,
                "epsilon_dissipation_mean": _mean(eps_viscous) + _mean(eps_drag) if finite_budget else None,
                "normalized_residual_mean": mean_residual,
                "normalized_residual_max": float(np.max(residuals)) if finite_budget else None,
            }
        )
        if finite_budget and mean_residual <= ENERGY_BALANCE_RESIDUAL_LIMIT:
            budget_status = "passed"
        elif finite_budget:
            budget_status = "failed"
            warnings.append("forced_energy_budget_residual_above_limit")
        else:
            warnings.append("non_finite_forcing_budget_metrics")
    else:
        warnings.append("forcing_budget_window_missing")

    stationarity_status = "failed"
    stationarity_summary: dict[str, Any] = {
        "transient_fraction": TRANSIENT_FRACTION,
        "relative_spread_limit": STATIONARITY_RELATIVE_SPREAD_LIMIT,
    }
    if averaging_window:
        energy = [float(row["energy"]) for row in averaging_window]
        enstrophy = [float(row["enstrophy"]) for row in averaging_window]
        if _finite_values(energy + enstrophy):
            energy_spread = _relative_spread(energy)
            enstrophy_spread = _relative_spread(enstrophy)
            stationarity_summary.update(
                {
                    "energy_relative_spread": energy_spread,
                    "enstrophy_relative_spread": enstrophy_spread,
                }
            )
            stationarity_status = (
                "passed"
                if energy_spread <= STATIONARITY_RELATIVE_SPREAD_LIMIT
                and enstrophy_spread <= STATIONARITY_RELATIVE_SPREAD_LIMIT
                else "warning"
            )
            if stationarity_status == "warning":
                warnings.append("statistical_stationarity_window_requires_human_review")
        else:
            warnings.append("non_finite_stationarity_metrics")

    spectral_status = "warning"
    spectral_summary: dict[str, Any] = {"status": "missing"}
    final_snapshot_path = output_dir / "snapshots" / f"vorticity_{config.time.steps:05d}.npy"
    if final_snapshot_path.exists():
        final_vorticity = np.load(final_snapshot_path)
        solver = NavierStokesSpectralSolver(
            grid=config.grid,
            physics=config.physics,
            time=config.time,
            forcing=config.forcing,
        )
        u_final, v_final = solver.velocity_from_vorticity(final_vorticity)
        spectrum = compute_velocity_energy_spectrum_2d(u_final, v_final, config.grid.lx, config.grid.ly)
        inverse_fit = _fit_slope(
            spectrum["radial_wavenumbers"],
            spectrum["radial_energy"],
            k_min=1.0,
            k_max=max(1.0, config.forcing.k_min - 0.5),
            label="reference_k_minus_5_over_3",
        )
        direct_fit = _fit_slope(
            spectrum["radial_wavenumbers"],
            spectrum["radial_energy"],
            k_min=config.forcing.k_max + 1.0,
            k_max=0.5 * float(max(spectrum["radial_wavenumbers"])),
            label="reference_k_minus_3",
        )
        spectral_summary = {
            "status": "diagnostic_only",
            "radial_wavenumbers": spectrum["radial_wavenumbers"],
            "radial_energy": spectrum["radial_energy"],
            "slope_fits": [inverse_fit, direct_fit],
            "warnings": inverse_fit.get("warnings", []) + direct_fit.get("warnings", []),
            "interpretation": "diagnostic_only_not_formal_cascade_validation",
        }
        spectral_status = "warning" if spectral_summary["warnings"] else "passed"
        warnings.extend(str(item) for item in spectral_summary["warnings"])
    else:
        warnings.append("final_snapshot_missing_for_spectral_diagnostics")

    if runtime_execution == "failed":
        accuracy_status = "failed"
    elif budget_status == "failed":
        accuracy_status = "failed"
    elif stationarity_status == "failed":
        accuracy_status = "failed"
    elif warnings:
        accuracy_status = "warning"
    else:
        accuracy_status = "passed"

    normalized = build_validation_result(
        validation_id=STUDY_NAME,
        validation_type="diagnostic",
        status="failed" if accuracy_status == "failed" else "warning" if warnings else "passed",
        claim_scope="diagnostic_only",
        parameters={
            "transient_fraction": TRANSIENT_FRACTION,
            "energy_balance_residual_limit": ENERGY_BALANCE_RESIDUAL_LIMIT,
            "stationarity_relative_spread_limit": STATIONARITY_RELATIVE_SPREAD_LIMIT,
        },
        metrics={
            "runtime_execution": runtime_execution,
            "accuracy_status": accuracy_status,
            "budget_status": budget_status,
            "stationarity_status": stationarity_status,
            "spectral_status": spectral_status,
        },
        thresholds={
            "normalized_energy_balance_residual_mean": ENERGY_BALANCE_RESIDUAL_LIMIT,
            "stationarity_relative_spread": STATIONARITY_RELATIVE_SPREAD_LIMIT,
            "minimum_slope_fit_points": MIN_SLOPE_FIT_POINTS,
        },
        artifacts={
            "summary_json": str(output_dir / "forced_turbulence_validation_summary.json"),
            "metrics_csv": str(run_result.get("metrics_csv", "")),
            "forcing_metrics_csv": str(run_result.get("forcing_metrics_csv", "")),
        },
        limitations=[
            "2d_periodic_forced_diagnostic_only",
            "not_formal_stationary_turbulence_validation",
            "not_a_3d_result",
            "not_a_millennium_problem_solution",
        ],
        notes=[
            "Energy-budget and spectral-slope diagnostics require human scientific review.",
            "Cascade slopes are diagnostic references only and are not proof of inertial ranges.",
        ],
    )

    payload = {
        **normalized,
        "study_name": STUDY_NAME,
        "created_at_utc": _utc_now(),
        "resolved_configuration": asdict(config),
        "acceptance_statuses": {
            "runtime_execution": runtime_execution,
            "accuracy_status": accuracy_status,
            "budget_status": budget_status,
            "stationarity_status": stationarity_status,
            "spectral_status": spectral_status,
            "scientific_acceptance": "human_review_required",
        },
        "budget_summary": budget_summary,
        "stationarity_summary": stationarity_summary,
        "spectral_summary": spectral_summary,
        "summary": {
            "unexpected_failures": unexpected_failures,
            "warnings": warnings,
        },
        "warnings": warnings,
        "scientific_acceptance": "human_review_required",
    }

    summary_path = output_dir / "forced_turbulence_validation_summary.json"
    summary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {"output_dir": output_dir, "summary_path": summary_path}
