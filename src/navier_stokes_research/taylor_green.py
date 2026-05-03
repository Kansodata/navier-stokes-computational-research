from __future__ import annotations

import json
from dataclasses import asdict
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
    status = "passed" if finite_metrics else "failed"

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
