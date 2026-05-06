from __future__ import annotations

import json
import math
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable

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
from navier_stokes_research.forcing_validator import MIN_SLOPE_FIT_POINTS, _fit_slope
from navier_stokes_research.runner import run_simulation
from navier_stokes_research.solver import NavierStokesSpectralSolver
from navier_stokes_research.spectral_diagnostics import compute_velocity_energy_spectrum_2d
from navier_stokes_research.validation_schema import build_validation_result

STUDY_NAME = "resolution_sensitivity_2d"
DEFAULT_RESOLUTIONS = (64, 128)
EXTENDED_RESOLUTIONS = (64, 128, 256, 512)
DIRECT_CASCADE_REFERENCE_SLOPE = -3.0
INVERSE_CASCADE_REFERENCE_SLOPE = -5.0 / 3.0
DIRECT_SLOPE_RELATIVE_ERROR_LIMIT = 0.5
DEFAULT_FINAL_TIME = 0.032
BASE_DT_AT_64 = 0.002


def _finite_number(value: Any) -> bool:
    return isinstance(value, (float, int)) and math.isfinite(float(value))


def _relative_slope_error(slope: float | None, reference: float) -> float | None:
    if slope is None:
        return None
    return float(abs(float(slope) - reference) / max(abs(reference), 1.0e-14))


def _orszag_component_cutoff(resolution: int) -> int:
    return int(math.floor(resolution / 3.0))


def _build_config(
    *,
    resolution: int,
    output_dir: Path,
    final_time: float,
) -> SimulationConfig:
    dt = BASE_DT_AT_64 * (64.0 / float(resolution))
    steps = max(4, int(round(final_time / dt)))
    return SimulationConfig(
        experiment_name=f"{STUDY_NAME}_n{resolution}",
        grid=GridConfig(nx=resolution, ny=resolution),
        time=TimeConfig(dt=dt, steps=steps, save_every=steps, cfl_safety=0.8, diffusion_safety=0.5),
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
            output_dir=str(output_dir),
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


def _final_spectrum(config: SimulationConfig) -> dict[str, Any]:
    snapshot_path = (
        Path(config.output.output_dir)
        / "snapshots"
        / f"vorticity_{config.time.steps:05d}.npy"
    )
    if not snapshot_path.exists():
        raise FileNotFoundError(f"Missing final vorticity snapshot: {snapshot_path}")
    final_vorticity = np.load(snapshot_path)
    solver = NavierStokesSpectralSolver(
        grid=config.grid,
        physics=config.physics,
        time=config.time,
        forcing=config.forcing,
    )
    u_final, v_final = solver.velocity_from_vorticity(final_vorticity)
    return compute_velocity_energy_spectrum_2d(
        u_final,
        v_final,
        config.grid.lx,
        config.grid.ly,
    )


def _run_resolution(
    *,
    resolution: int,
    root: Path,
    final_time: float,
) -> dict[str, Any]:
    output_dir = root / f"n{resolution}"
    config = _build_config(
        resolution=resolution,
        output_dir=output_dir,
        final_time=final_time,
    )
    result = run_simulation(config, validate=True)
    metrics = result.get("metrics", [])
    forcing_metrics = result.get("forcing_metrics", [])
    if not isinstance(metrics, list) or not metrics:
        raise RuntimeError("missing_metrics")
    if not isinstance(forcing_metrics, list) or not forcing_metrics:
        raise RuntimeError("missing_forcing_metrics")

    spectrum = _final_spectrum(config)
    k_cut = _orszag_component_cutoff(resolution)
    direct_k_min = float(config.forcing.k_max + 1.0)
    direct_k_max = max(direct_k_min, float(0.8 * k_cut))
    inverse_k_min = 1.0
    inverse_k_max = max(inverse_k_min, float(config.forcing.k_min - 0.5))

    inverse_fit = _fit_slope(
        spectrum["radial_wavenumbers"],
        spectrum["radial_energy"],
        k_min=inverse_k_min,
        k_max=inverse_k_max,
        label="reference_k_minus_5_over_3",
    )
    direct_fit = _fit_slope(
        spectrum["radial_wavenumbers"],
        spectrum["radial_energy"],
        k_min=direct_k_min,
        k_max=direct_k_max,
        label="reference_k_minus_3",
    )
    direct_error = _relative_slope_error(
        direct_fit.get("slope"),
        DIRECT_CASCADE_REFERENCE_SLOPE,
    )
    inverse_error = _relative_slope_error(
        inverse_fit.get("slope"),
        INVERSE_CASCADE_REFERENCE_SLOPE,
    )
    final_metrics = metrics[-1]
    budget_window = forcing_metrics[max(0, len(forcing_metrics) // 2) :]
    residuals = [float(row["energy_balance_residual_normalized"]) for row in budget_window]
    mean_budget_residual = float(np.mean(np.asarray(residuals, dtype=float))) if residuals else None
    warnings = []
    warnings.extend(str(item) for item in direct_fit.get("warnings", []))
    warnings.extend(str(item) for item in inverse_fit.get("warnings", []))
    if direct_error is None:
        warnings.append("direct_cascade_slope_unavailable")
    elif direct_error > DIRECT_SLOPE_RELATIVE_ERROR_LIMIT:
        warnings.append("direct_cascade_slope_relative_error_above_limit")
    if direct_k_max >= float(k_cut):
        warnings.append("direct_fit_reaches_orszag_cutoff")

    finite_metrics = all(
        _finite_number(value)
        for value in (
            final_metrics.get("energy"),
            final_metrics.get("enstrophy"),
            final_metrics.get("max_velocity"),
            final_metrics.get("cfl"),
            mean_budget_residual,
        )
    )
    status = "passed" if finite_metrics and not warnings else "warning" if finite_metrics else "failed"
    return {
        "resolution": resolution,
        "dt": float(config.time.dt),
        "steps": int(config.time.steps),
        "final_time": float(config.time.dt * config.time.steps),
        "final_energy": float(final_metrics["energy"]),
        "final_enstrophy": float(final_metrics["enstrophy"]),
        "final_max_velocity": float(final_metrics["max_velocity"]),
        "cfl_peak": float(max(float(row["cfl"]) for row in metrics)),
        "mean_energy_budget_residual_normalized": mean_budget_residual,
        "orszag_component_cutoff_k": k_cut,
        "direct_fit_k_range": {"k_min": direct_k_min, "k_max": direct_k_max},
        "inverse_fit_k_range": {"k_min": inverse_k_min, "k_max": inverse_k_max},
        "direct_cascade_slope_fit": direct_fit,
        "inverse_cascade_slope_fit": inverse_fit,
        "direct_cascade_slope_relative_error": direct_error,
        "inverse_cascade_slope_relative_error": inverse_error,
        "status": status,
        "warnings": warnings,
        "resolved_configuration": asdict(config),
    }


def _recommend_resolution(runs: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = []
    for run in runs:
        direct_error = run.get("direct_cascade_slope_relative_error")
        direct_fit = run.get("direct_cascade_slope_fit", {})
        if (
            _finite_number(direct_error)
            and float(direct_error) <= DIRECT_SLOPE_RELATIVE_ERROR_LIMIT
            and isinstance(direct_fit, dict)
            and int(direct_fit.get("fit_points", 0)) >= MIN_SLOPE_FIT_POINTS
        ):
            candidates.append(run)
    if candidates:
        best = min(candidates, key=lambda item: int(item["resolution"]))
        return {
            "status": "candidate_identified",
            "minimum_resolution_for_direct_cascade_diagnostic": int(best["resolution"]),
            "basis": (
                "First tested resolution with finite direct-cascade slope fit, enough fit points, "
                "and relative slope error below the diagnostic threshold."
            ),
        }
    return {
        "status": "not_identified",
        "minimum_resolution_for_direct_cascade_diagnostic": None,
        "basis": (
            "No tested resolution produced a direct-cascade slope fit that satisfied the "
            "diagnostic relative-error threshold. This is a warning, not a failed solver claim."
        ),
    }


def run_resolution_sensitivity_study_2d(
    *,
    base_output_dir: str = "outputs/benchmarks",
    resolutions: Iterable[int] = DEFAULT_RESOLUTIONS,
    final_time: float = DEFAULT_FINAL_TIME,
) -> dict[str, Path]:
    root = Path(base_output_dir) / STUDY_NAME
    root.mkdir(parents=True, exist_ok=True)
    resolution_list = [int(item) for item in resolutions]
    if not resolution_list:
        raise ValueError("At least one resolution is required.")
    if any(item < 16 for item in resolution_list):
        raise ValueError("Resolution sensitivity study requires N >= 16.")

    runs: list[dict[str, Any]] = []
    unexpected_failures: list[str] = []
    for resolution in resolution_list:
        try:
            runs.append(_run_resolution(resolution=resolution, root=root, final_time=final_time))
        except Exception as exc:  # noqa: BLE001
            unexpected_failures.append(f"n{resolution}:{type(exc).__name__}")
            runs.append(
                {
                    "resolution": resolution,
                    "status": "failed",
                    "warnings": [f"runtime_exception:{type(exc).__name__}"],
                }
            )

    recommendation = _recommend_resolution(runs)
    failed = any(run.get("status") == "failed" for run in runs)
    warned = any(run.get("status") == "warning" for run in runs)
    sensitivity_status = "failed" if failed else "warning" if warned else "passed"
    global_status = "failed" if failed else "warning" if warned or recommendation["status"] == "not_identified" else "passed"

    normalized = build_validation_result(
        validation_id=STUDY_NAME,
        validation_type="diagnostic",
        status=global_status,
        claim_scope="diagnostic_only",
        parameters={
            "resolutions": resolution_list,
            "final_time": final_time,
            "reference_slopes": {
                "inverse_cascade": INVERSE_CASCADE_REFERENCE_SLOPE,
                "direct_cascade": DIRECT_CASCADE_REFERENCE_SLOPE,
            },
        },
        metrics={
            "runtime_execution": "failed" if failed else "passed",
            "sensitivity_status": sensitivity_status,
            "recommendation_status": recommendation["status"],
        },
        thresholds={
            "direct_slope_relative_error_limit": DIRECT_SLOPE_RELATIVE_ERROR_LIMIT,
            "minimum_slope_fit_points": MIN_SLOPE_FIT_POINTS,
        },
        artifacts={
            "summary_json": str(root / "resolution_sensitivity_summary.json"),
        },
        limitations=[
            "2d_periodic_forced_diagnostic_only",
            "not_formal_stationary_turbulence_validation",
            "not_a_3d_result",
            "not_a_millennium_problem_solution",
            "not_a_mathematical_proof",
        ],
        notes=[
            "Resolution sensitivity estimates are diagnostics for experimental design.",
            "Kraichnan-Leith-Batchelor reference slopes are not treated as automatic proof.",
        ],
    )
    payload = {
        **normalized,
        "study_name": STUDY_NAME,
        "resolutions": runs,
        "acceptance_statuses": {
            "runtime_execution": "failed" if failed else "passed",
            "sensitivity_status": sensitivity_status,
            "scientific_acceptance": "human_review_required",
        },
        "recommendation": recommendation,
        "summary": {
            "unexpected_failures": unexpected_failures,
            "warnings": [
                warning
                for run in runs
                for warning in run.get("warnings", [])
                if isinstance(warning, str)
            ],
        },
        "scientific_acceptance": "human_review_required",
    }
    summary_path = root / "resolution_sensitivity_summary.json"
    summary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {"output_dir": root, "summary_path": summary_path}
