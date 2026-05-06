from __future__ import annotations

import json
import math
import os
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy as np

from navier_stokes_research.config import GridConfig, InitialConditionConfig, PhysicsConfig, TimeConfig
from navier_stokes_research.initial_conditions import create_initial_vorticity
from navier_stokes_research.solver import NavierStokesSpectralSolver, SpectralSolver512

BENCHMARK_NAME = "hpc_fftw_benchmark"
DEFAULT_RESOLUTION = 512
DEFAULT_STEPS_SAFE = 2
DEFAULT_STEPS_EXTENDED = 12
DEFAULT_DT_SAFE = 1.0e-4
DEFAULT_CFL_LIMIT = 0.8
DEFAULT_VISCOSITY = 0.001
DEFAULT_INIT_CONDITION = InitialConditionConfig(
    kind="vortices",
    amplitude=0.8,
    smoothing_sigma=6.0,
    seed=2026,
    vortex_radius=0.35,
    vortex_strength=6.0,
    vortex_distance=1.2,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite(value: Any) -> bool:
    return isinstance(value, (float, int)) and math.isfinite(float(value))


def _energy_enstrophy(vorticity: np.ndarray, u: np.ndarray, v: np.ndarray, dx: float, dy: float) -> tuple[float, float]:
    cell = dx * dy
    energy = 0.5 * float(np.sum(u * u + v * v) * cell)
    enstrophy = 0.5 * float(np.sum(vorticity * vorticity) * cell)
    return energy, enstrophy


def _baseline_metrics(
    *,
    resolution: int,
    steps: int,
    dt: float,
    viscosity: float,
    cfl_limit: float,
    initial_vorticity: np.ndarray,
) -> dict[str, Any]:
    grid = GridConfig(nx=resolution, ny=resolution)
    physics = PhysicsConfig(viscosity=viscosity)
    time_cfg = TimeConfig(
        dt=dt,
        steps=steps,
        save_every=max(1, steps),
        cfl_safety=cfl_limit,
        diffusion_safety=0.5,
    )
    init_start = perf_counter()
    solver = NavierStokesSpectralSolver(grid=grid, physics=physics, time=time_cfg)
    initialization = perf_counter() - init_start

    omega = np.array(initial_vorticity, dtype=float, copy=True)
    max_cfl = 0.0
    run_start = perf_counter()
    warnings: list[str] = []
    status = "passed"
    try:
        for _ in range(steps):
            omega, state = solver.step(omega)
            max_cfl = max(max_cfl, float(state.cfl_number))
            if state.cfl_number >= cfl_limit:
                raise FloatingPointError("baseline_cfl_violation")
        u, v = solver.velocity_from_vorticity(omega)
        final_energy, final_enstrophy = _energy_enstrophy(omega, u, v, solver.dx, solver.dy)
    except Exception as exc:  # noqa: BLE001
        status = "failed"
        warnings.append(f"runtime_exception:{type(exc).__name__}")
        final_energy = float("nan")
        final_enstrophy = float("nan")
    total_runtime = perf_counter() - run_start

    if not (_finite(final_energy) and _finite(final_enstrophy)):
        status = "failed"
        warnings.append("non_finite_terminal_metrics")

    return {
        "solver_name": "baseline_numpy_fft",
        "resolution": resolution,
        "steps": steps,
        "dt": dt,
        "final_time": dt * steps,
        "initialization_time_seconds": initialization,
        "total_runtime_seconds": total_runtime,
        "average_step_time_seconds": total_runtime / max(steps, 1),
        "final_energy": final_energy,
        "final_enstrophy": final_enstrophy,
        "max_cfl": max_cfl,
        "status": status,
        "warnings": warnings,
    }


def _fftw_metrics(
    *,
    resolution: int,
    steps: int,
    dt: float,
    viscosity: float,
    cfl_limit: float,
    initial_vorticity: np.ndarray,
    fftw_effort: str,
) -> dict[str, Any]:
    warnings: list[str] = []
    if resolution != 512:
        return {
            "solver_name": "fftw_opt_in_solver512",
            "resolution": resolution,
            "steps": steps,
            "dt": dt,
            "final_time": dt * steps,
            "initialization_time_seconds": None,
            "total_runtime_seconds": None,
            "average_step_time_seconds": None,
            "final_energy": None,
            "final_enstrophy": None,
            "max_cfl": None,
            "status": "skipped",
            "warnings": ["fftw_solver512_requires_resolution_512"],
        }

    init_start = perf_counter()
    try:
        solver = SpectralSolver512(
            viscosity=viscosity,
            dt=dt,
            cfl_safety=cfl_limit,
            nx=resolution,
            ny=resolution,
            fftw_effort=fftw_effort,
            spectrum_interval=max(1, steps),
        )
    except Exception as exc:  # noqa: BLE001
        return {
            "solver_name": "fftw_opt_in_solver512",
            "resolution": resolution,
            "steps": steps,
            "dt": dt,
            "final_time": dt * steps,
            "initialization_time_seconds": None,
            "total_runtime_seconds": None,
            "average_step_time_seconds": None,
            "final_energy": None,
            "final_enstrophy": None,
            "max_cfl": None,
            "status": "failed",
            "warnings": [f"solver_initialization_exception:{type(exc).__name__}"],
        }
    initialization = perf_counter() - init_start

    run_start = perf_counter()
    status = "passed"
    try:
        solver.set_vorticity(np.array(initial_vorticity, dtype=float, copy=True))
        for _ in range(steps):
            solver.step()
        final_energy = float(solver.energy())
        final_enstrophy = float(solver.enstrophy())
        max_cfl = max((sample.cfl_number for sample in solver.audit_log), default=0.0)
    except Exception as exc:  # noqa: BLE001
        status = "failed"
        warnings.append(f"runtime_exception:{type(exc).__name__}")
        final_energy = float("nan")
        final_enstrophy = float("nan")
        max_cfl = float("nan")
    total_runtime = perf_counter() - run_start

    if not (_finite(final_energy) and _finite(final_enstrophy) and _finite(max_cfl)):
        status = "failed"
        warnings.append("non_finite_terminal_metrics")

    return {
        "solver_name": "fftw_opt_in_solver512",
        "resolution": resolution,
        "steps": steps,
        "dt": dt,
        "final_time": dt * steps,
        "initialization_time_seconds": initialization,
        "total_runtime_seconds": total_runtime,
        "average_step_time_seconds": total_runtime / max(steps, 1),
        "final_energy": final_energy,
        "final_enstrophy": final_enstrophy,
        "max_cfl": max_cfl,
        "status": status,
        "warnings": warnings,
        "fftw_effort": fftw_effort,
        "threads": int(max(1, os.cpu_count() or 1)),
    }


def _relative_difference(a: Any, b: Any) -> float | None:
    if not (_finite(a) and _finite(b)):
        return None
    fa = float(a)
    fb = float(b)
    denom = max(abs(fa), abs(fb), 1.0e-14)
    return abs(fa - fb) / denom


def run_hpc_fftw_benchmark(
    *,
    base_output_dir: str = "outputs/benchmarks",
    resolution: int = DEFAULT_RESOLUTION,
    steps: int = DEFAULT_STEPS_SAFE,
    dt: float = DEFAULT_DT_SAFE,
    viscosity: float = DEFAULT_VISCOSITY,
    cfl_limit: float = DEFAULT_CFL_LIMIT,
    extended: bool = False,
    fftw_effort: str = "FFTW_MEASURE",
) -> dict[str, Path]:
    if extended:
        steps = max(steps, DEFAULT_STEPS_EXTENDED)
    benchmark_root = Path(base_output_dir) / BENCHMARK_NAME
    benchmark_root.mkdir(parents=True, exist_ok=True)
    summary_path = benchmark_root / "hpc_fftw_benchmark_summary.json"

    init_cfg = DEFAULT_INIT_CONDITION
    grid = GridConfig(nx=resolution, ny=resolution)
    initial_vorticity = create_initial_vorticity(init_cfg, grid)

    baseline = _baseline_metrics(
        resolution=resolution,
        steps=steps,
        dt=dt,
        viscosity=viscosity,
        cfl_limit=cfl_limit,
        initial_vorticity=initial_vorticity,
    )
    fftw = _fftw_metrics(
        resolution=resolution,
        steps=steps,
        dt=dt,
        viscosity=viscosity,
        cfl_limit=cfl_limit,
        initial_vorticity=initial_vorticity,
        fftw_effort=fftw_effort,
    )

    warnings: list[str] = []
    warnings.extend(str(item) for item in baseline.get("warnings", []))
    warnings.extend(str(item) for item in fftw.get("warnings", []))

    speedup_ratio = None
    baseline_runtime = baseline.get("total_runtime_seconds")
    fftw_runtime = fftw.get("total_runtime_seconds")
    if _finite(baseline_runtime) and _finite(fftw_runtime) and float(fftw_runtime) > 0.0:
        speedup_ratio = float(baseline_runtime) / float(fftw_runtime)
    else:
        warnings.append("speedup_ratio_unavailable")

    energy_relative_difference = _relative_difference(
        baseline.get("final_energy"), fftw.get("final_energy")
    )
    enstrophy_relative_difference = _relative_difference(
        baseline.get("final_enstrophy"), fftw.get("final_enstrophy")
    )
    cfl_relative_difference = _relative_difference(
        baseline.get("max_cfl"), fftw.get("max_cfl")
    )

    baseline_ok = baseline.get("status") == "passed"
    fftw_ok = fftw.get("status") == "passed"
    if not baseline_ok or not fftw_ok:
        consistency_status = "failed"
        performance_status = "failed"
        benchmark_status = "failed"
        execution_status = "failed"
    else:
        consistency_status = "passed"
        if any(value is None for value in (energy_relative_difference, enstrophy_relative_difference, cfl_relative_difference)):
            consistency_status = "warning"
            warnings.append("consistency_metrics_unavailable")
        performance_status = "passed" if speedup_ratio is not None else "warning"
        benchmark_status = "warning" if "warning" in {consistency_status, performance_status} else "passed"
        execution_status = "passed"

    comparison = {
        "speedup_ratio": speedup_ratio,
        "energy_relative_difference": energy_relative_difference,
        "enstrophy_relative_difference": enstrophy_relative_difference,
        "cfl_relative_difference": cfl_relative_difference,
        "consistency_status": consistency_status,
        "performance_status": performance_status,
    }
    payload = {
        "schema_version": "1.0",
        "benchmark_name": BENCHMARK_NAME,
        "created_at_utc": _utc_now(),
        "scientific_scope": "2d_incompressible_periodic_navier_stokes_only",
        "scientific_acceptance": "human_review_required",
        "execution_status": execution_status,
        "benchmark_status": benchmark_status,
        "warnings": sorted(set(warnings)),
        "baseline_solver": baseline,
        "fftw_solver": fftw,
        "comparison": comparison,
        "environment": {
            "python_version": os.sys.version,
            "platform": os.name,
            "cpu_count": int(max(1, os.cpu_count() or 1)),
        },
        "parameters": {
            "resolution": resolution,
            "steps": steps,
            "dt": dt,
            "viscosity": viscosity,
            "cfl_limit": cfl_limit,
            "extended_mode": extended,
            "fftw_effort": fftw_effort,
            "initial_condition": asdict(init_cfg),
        },
        "rollback_note": "git revert <merge_commit_of_this_pr>",
        "limitations": [
            "infrastructure_benchmark_only_not_new_physics_validation",
            "not_a_3d_result",
            "not_a_millennium_problem_solution",
            "not_a_mathematical_proof",
        ],
    }
    summary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {"output_dir": benchmark_root, "summary_path": summary_path}
