from __future__ import annotations

import csv
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
from navier_stokes_research.initial_conditions import create_initial_vorticity
from navier_stokes_research.solver import NavierStokesSpectralSolver

TWO_PI = 2.0 * np.pi
EPSILON = 1e-12
ROUND_OFF_ERROR_FLOOR = 1e-12
DEFAULT_TAYLOR_GREEN_ACCURACY_TOLERANCES = {
    "l2": 1e-10,
    "linf": 1e-10,
    "relative": 1e-10,
}
DEFAULT_TAYLOR_GREEN_CONVERGENCE_RESOLUTIONS = (32, 64, 128, 256)


def _build_grid_coordinates(grid: GridConfig) -> tuple[np.ndarray, np.ndarray]:
    x = np.linspace(0.0, grid.lx, grid.nx, endpoint=False)
    y = np.linspace(0.0, grid.ly, grid.ny, endpoint=False)
    return np.meshgrid(x, y, indexing="ij")


def taylor_green_velocity_exact(
    grid: GridConfig,
    viscosity: float,
    time_value: float,
    amplitude: float = 1.0,
) -> tuple[np.ndarray, np.ndarray]:
    xx, yy = _build_grid_coordinates(grid)
    decay = np.exp(-2.0 * viscosity * time_value)
    u = amplitude * np.sin(xx) * np.cos(yy) * decay
    v = -amplitude * np.cos(xx) * np.sin(yy) * decay
    return u, v


def _safe_relative_error(l2_error: float, l2_reference: float) -> float | None:
    if not np.isfinite(l2_error) or not np.isfinite(l2_reference):
        return None
    if l2_reference <= EPSILON:
        return None
    return float(l2_error / l2_reference)


def _safe_error_convergence_order(
    coarse_error: float | None,
    fine_error: float | None,
    refinement_ratio: float,
    epsilon: float = 1e-14,
) -> float | None:
    """Estimate convergence order from exact/reference errors.

    Uses p = log(error_coarse / error_fine) / log(r). Negative values are
    intentionally preserved because they reveal error growth under refinement.
    """
    if coarse_error is None or fine_error is None:
        return None
    if refinement_ratio <= 1.0:
        return None
    if not np.isfinite(coarse_error) or not np.isfinite(fine_error):
        return None
    effective_floor = max(epsilon, ROUND_OFF_ERROR_FLOOR)
    if coarse_error <= effective_floor or fine_error <= effective_floor:
        return None
    return float(math.log(coarse_error / fine_error) / math.log(refinement_ratio))


def _compute_error_metrics(
    numerical_u: np.ndarray,
    numerical_v: np.ndarray,
    exact_u: np.ndarray,
    exact_v: np.ndarray,
) -> dict[str, float | None]:
    du = numerical_u - exact_u
    dv = numerical_v - exact_v
    error_mag = np.sqrt(du**2 + dv**2)
    ref_mag = np.sqrt(exact_u**2 + exact_v**2)

    l2_error = float(np.sqrt(np.mean(error_mag**2)))
    linf_error = float(np.max(np.abs(error_mag)))
    l2_reference = float(np.sqrt(np.mean(ref_mag**2)))
    return {
        "l2": l2_error,
        "linf": linf_error,
        "relative": _safe_relative_error(l2_error, l2_reference),
        "l2_reference": l2_reference,
    }


def _validate_taylor_green_inputs(
    grid: GridConfig,
    viscosity: float,
    final_time: float,
) -> None:
    if grid.nx <= 0 or grid.ny <= 0:
        raise ValueError("Grid resolution must be positive in both directions.")
    if viscosity <= 0.0:
        raise ValueError("Viscosity must be strictly positive for Taylor-Green validation.")
    if final_time < 0.0:
        raise ValueError("Final physical time must be non-negative.")
    if not np.isclose(grid.lx, TWO_PI, atol=1e-12) or not np.isclose(grid.ly, TWO_PI, atol=1e-12):
        raise ValueError("Taylor-Green validation requires a [0, 2pi] x [0, 2pi] periodic domain.")


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temp_path.replace(path)


def _evaluate_accuracy_status(
    errors: dict[str, float | None],
    tolerances: dict[str, float] | None = None,
) -> tuple[str, list[str]]:
    warnings: list[str] = []
    if not tolerances:
        warnings.append("no_explicit_accuracy_tolerances_configured")
        return "warning", warnings

    checks: list[bool] = []
    for key in ("l2", "linf", "relative"):
        if key not in tolerances:
            continue
        value = errors.get(key)
        limit = tolerances[key]
        if value is None or not np.isfinite(value):
            checks.append(False)
            continue
        checks.append(bool(value <= limit))

    if not checks:
        warnings.append("tolerances_defined_but_no_matching_metrics")
        return "not_evaluated", warnings
    return ("passed", warnings) if all(checks) else ("failed", warnings)


def build_taylor_green_config(
    base_output_dir: str = "outputs/benchmarks",
    resolution: int = 64,
    viscosity: float = 0.001,
    final_time: float = 0.24,
    dt: float = 0.0015,
) -> SimulationConfig:
    steps = max(1, int(round(final_time / dt)))
    output_dir = f"{base_output_dir}/taylor_green_2d"
    return SimulationConfig(
        experiment_name="validation_taylor_green_2d",
        grid=GridConfig(nx=resolution, ny=resolution, lx=float(TWO_PI), ly=float(TWO_PI)),
        time=TimeConfig(
            dt=dt,
            steps=steps,
            save_every=max(1, steps // 4),
            cfl_safety=0.8,
            diffusion_safety=0.5,
        ),
        physics=PhysicsConfig(viscosity=viscosity),
        initial_condition=InitialConditionConfig(
            kind="taylor_green_2d",
            amplitude=1.0,
            seed=2026,
        ),
        output=OutputConfig(
            output_dir=output_dir,
            save_plots=False,
            save_snapshots=False,
            log_level="INFO",
        ),
    )


def run_taylor_green_validation(base_output_dir: str = "outputs/benchmarks") -> dict[str, Path | dict[str, Any]]:
    config = build_taylor_green_config(base_output_dir=base_output_dir)
    _validate_taylor_green_inputs(config.grid, config.physics.viscosity, config.time.steps * config.time.dt)

    solver = NavierStokesSpectralSolver(grid=config.grid, physics=config.physics, time=config.time)
    vorticity = create_initial_vorticity(config.initial_condition, config.grid)
    solver.ensure_stability(vorticity)

    for _ in range(config.time.steps):
        vorticity, _ = solver.step(vorticity)

    numerical_u, numerical_v = solver.velocity_from_vorticity(vorticity)
    final_time = config.time.steps * config.time.dt
    exact_u, exact_v = taylor_green_velocity_exact(config.grid, config.physics.viscosity, final_time)
    errors = _compute_error_metrics(numerical_u, numerical_v, exact_u, exact_v)

    finite_metrics = all(
        np.isfinite(value)
        for key, value in errors.items()
        if key != "relative" and value is not None
    )
    if errors["relative"] is not None:
        finite_metrics = finite_metrics and bool(np.isfinite(errors["relative"]))
    execution_status = "passed" if finite_metrics else "failed"
    accuracy_status, warnings = _evaluate_accuracy_status(
        errors=errors,
        tolerances=DEFAULT_TAYLOR_GREEN_ACCURACY_TOLERANCES,
    )
    if execution_status == "passed":
        warnings.append("status_passed_reflects_runtime_execution_not_scientific_acceptance")
    warnings.append("taylor_green_2d_controlled_case_not_a_3d_existence_smoothness_proof")
    status = execution_status

    report: dict[str, Any] = {
        "resolved_configuration": asdict(config),
        "domain": {"x": [0.0, float(TWO_PI)], "y": [0.0, float(TWO_PI)]},
        "resolution": {"nx": config.grid.nx, "ny": config.grid.ny},
        "viscosity": float(config.physics.viscosity),
        "final_physical_time": float(final_time),
        "errors": {
            "l2": errors["l2"],
            "linf": errors["linf"],
            "relative": errors["relative"],
        },
        "status": status,
        "execution_status": execution_status,
        "accuracy_status": accuracy_status,
        "warnings": warnings,
        "notes": [
            "Validacion numerica controlada 2D con solucion analitica de Taylor-Green.",
            "Este resultado no prueba existencia/suavidad global del problema 3D de Navier-Stokes.",
        ],
    }

    report_path = Path(config.output.output_dir) / "taylor_green_validation.json"
    _write_json_atomic(report_path, report)
    return {
        "report": report,
        "report_path": report_path,
        "output_dir": Path(config.output.output_dir),
    }


def _write_taylor_green_convergence_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "resolution",
        "dt",
        "steps",
        "final_time",
        "l2_error",
        "linf_error",
        "relative_error",
        "l2_order_vs_previous",
        "linf_order_vs_previous",
        "relative_order_vs_previous",
        "execution_status",
        "accuracy_status",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_taylor_green_convergence_study(
    *,
    base_output_dir: str = "outputs/benchmarks",
    study_name: str = "taylor_green_convergence_2d",
    resolutions: tuple[int, ...] = DEFAULT_TAYLOR_GREEN_CONVERGENCE_RESOLUTIONS,
    base_resolution: int = 64,
    base_dt: float = 0.0015,
    final_time: float = 0.24,
    viscosity: float = 0.001,
) -> dict[str, Path]:
    """Run Taylor-Green validation across resolutions and estimate error orders.

    This is a numerical verification harness for the controlled 2D analytical
    Taylor-Green case. It does not claim anything about the 3D Millennium problem.
    """
    if len(resolutions) < 2:
        raise ValueError("At least two resolutions are required.")
    if any(value <= 0 for value in resolutions):
        raise ValueError("All resolutions must be positive integers.")

    sorted_resolutions = tuple(sorted(set(resolutions)))
    study_dir = Path(base_output_dir) / study_name
    study_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    runs: list[dict[str, Any]] = []
    previous: dict[str, Any] | None = None

    for resolution in sorted_resolutions:
        dt = base_dt * (base_resolution / resolution)
        config = build_taylor_green_config(
            base_output_dir=str(study_dir / f"n{resolution}"),
            resolution=resolution,
            viscosity=viscosity,
            final_time=final_time,
            dt=dt,
        )

        _validate_taylor_green_inputs(config.grid, config.physics.viscosity, config.time.steps * config.time.dt)

        solver = NavierStokesSpectralSolver(grid=config.grid, physics=config.physics, time=config.time)
        vorticity = create_initial_vorticity(config.initial_condition, config.grid)
        solver.ensure_stability(vorticity)

        for _ in range(config.time.steps):
            vorticity, _ = solver.step(vorticity)

        numerical_u, numerical_v = solver.velocity_from_vorticity(vorticity)
        physical_time = config.time.steps * config.time.dt
        exact_u, exact_v = taylor_green_velocity_exact(config.grid, config.physics.viscosity, physical_time)
        errors = _compute_error_metrics(numerical_u, numerical_v, exact_u, exact_v)
        execution_status = "passed" if all(
            value is None or np.isfinite(value)
            for value in errors.values()
        ) else "failed"
        accuracy_status, warnings = _evaluate_accuracy_status(
        errors=errors,
        tolerances=DEFAULT_TAYLOR_GREEN_ACCURACY_TOLERANCES,
    )
        warnings.append("taylor_green_convergence_is_numerical_verification_not_3d_proof")

        l2_order = None
        linf_order = None
        relative_order = None
        if previous is not None:
            refinement_ratio = resolution / int(previous["resolution"])
            l2_order = _safe_error_convergence_order(previous["l2_error"], errors["l2"], refinement_ratio)
            linf_order = _safe_error_convergence_order(previous["linf_error"], errors["linf"], refinement_ratio)
            relative_order = _safe_error_convergence_order(previous["relative_error"], errors["relative"], refinement_ratio)

        row = {
            "resolution": resolution,
            "dt": config.time.dt,
            "steps": config.time.steps,
            "final_time": physical_time,
            "l2_error": errors["l2"],
            "linf_error": errors["linf"],
            "relative_error": errors["relative"],
            "l2_order_vs_previous": l2_order,
            "linf_order_vs_previous": linf_order,
            "relative_order_vs_previous": relative_order,
            "execution_status": execution_status,
            "accuracy_status": accuracy_status,
        }
        rows.append(row)
        previous = row

        run_payload = {
            "resolution": resolution,
            "resolved_configuration": asdict(config),
            "errors": {
                "l2": errors["l2"],
                "linf": errors["linf"],
                "relative": errors["relative"],
                "l2_reference": errors["l2_reference"],
            },
            "orders_vs_previous": {
                "l2": l2_order,
                "linf": linf_order,
                "relative": relative_order,
            },
            "execution_status": execution_status,
            "accuracy_status": accuracy_status,
            "warnings": warnings,
        }
        run_path = Path(config.output.output_dir) / "taylor_green_validation.json"
        _write_json_atomic(run_path, run_payload)
        runs.append({**run_payload, "report_path": str(run_path)})

    orders = [
        {
            "from_resolution": rows[idx - 1]["resolution"],
            "to_resolution": rows[idx]["resolution"],
            "l2_order": rows[idx]["l2_order_vs_previous"],
            "linf_order": rows[idx]["linf_order_vs_previous"],
            "relative_order": rows[idx]["relative_order_vs_previous"],
        }
        for idx in range(1, len(rows))
    ]

    all_errors_at_roundoff_floor = all(
        row["l2_error"] <= ROUND_OFF_ERROR_FLOOR
        and row["linf_error"] <= DEFAULT_TAYLOR_GREEN_ACCURACY_TOLERANCES["linf"]
        and row["relative_error"] <= ROUND_OFF_ERROR_FLOOR
        for row in rows
    )
    all_accuracy_passed = all(row["accuracy_status"] == "passed" for row in rows)
    formal_error_convergence_status = (
        "passed_roundoff_floor"
        if all_errors_at_roundoff_floor and all_accuracy_passed
        else "human_review_required"
    )

    summary = {
        "study_name": study_name,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": {
            "case": "2d_taylor_green_analytical_velocity",
            "error_metrics": ["l2", "linf", "relative_l2"],
            "order_formula": "p = log(error_coarse / error_fine) / log(N_fine / N_coarse)",
            "dt_scaling_rule": "dt = base_dt * (base_resolution / resolution)",
        },
        "inputs": {
            "resolutions": list(sorted_resolutions),
            "base_resolution": base_resolution,
            "base_dt": base_dt,
            "target_final_time": final_time,
            "viscosity": viscosity,
        },
        "runs": runs,
        "orders": orders,
        "acceptance_statuses": {
            "runtime_execution": "passed" if all(row["execution_status"] == "passed" for row in rows) else "failed",
            "formal_error_convergence": formal_error_convergence_status,
            "scientific_acceptance": "human_review_required",
            "scientific_acceptance_reasons": [
                "controlled_2d_case_only",
                "not_a_3d_existence_or_smoothness_proof",
                "passed_roundoff_floor_means_analytical_2d_case_matches_to_machine_precision"
                if formal_error_convergence_status == "passed_roundoff_floor"
                else "orders_must_be_reviewed_for_monotonicity_and_expected_rate",
            ],
        },
        "notes": [
            "Este estudio usa una solucion analitica 2D para estimar errores por resolucion.",
            "La aceptacion cientifica requiere revisar monotonicidad de errores y orden esperado.",
        ],
    }

    summary_path = study_dir / "taylor_green_convergence_summary.json"
    csv_path = study_dir / "taylor_green_convergence_metrics.csv"
    _write_json_atomic(summary_path, summary)
    _write_taylor_green_convergence_csv(rows, csv_path)

    return {
        "study_dir": study_dir,
        "summary_path": summary_path,
        "metrics_csv_path": csv_path,
    }
