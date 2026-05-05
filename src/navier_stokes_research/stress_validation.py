from __future__ import annotations

import json
from dataclasses import asdict, dataclass
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
from navier_stokes_research.runner import run_simulation
from navier_stokes_research.solver import NavierStokesSpectralSolver
from navier_stokes_research.spectral_diagnostics import compute_velocity_energy_spectrum_2d

SCENARIO_STATUSES = {"passed", "warning", "failed", "expected_fail_closed"}
STUDY_NAME = "stress_validation_2d"


@dataclass(frozen=True)
class StressScenarioSpec:
    name: str
    nx: int = 32
    ny: int = 32
    viscosity: float = 0.001
    amplitude: float = 1.0
    smoothing_sigma: float = 3.0
    seed: int = 42
    steps: int = 24
    target_initial_cfl: float = 0.25
    cfl_safety: float = 0.8
    diffusion_safety: float = 0.5
    expected_failure_reason: str | None = None
    diagnostic_note: str = ""


def _base_output_path(base_output_dir: str | Path) -> Path:
    return Path(base_output_dir) / STUDY_NAME


def _build_config(spec: StressScenarioSpec, output_dir: Path) -> SimulationConfig:
    grid = GridConfig(nx=spec.nx, ny=spec.ny, lx=2.0 * np.pi, ly=2.0 * np.pi)
    initial_condition = InitialConditionConfig(
        kind="random",
        amplitude=spec.amplitude,
        smoothing_sigma=spec.smoothing_sigma,
        seed=spec.seed,
    )
    physics = PhysicsConfig(viscosity=spec.viscosity)
    time_for_dt_estimate = TimeConfig(
        dt=1.0,
        steps=spec.steps,
        save_every=max(spec.steps, 1),
        cfl_safety=spec.cfl_safety,
        diffusion_safety=spec.diffusion_safety,
    )
    dt = _dt_for_target_initial_cfl(
        grid=grid,
        physics=physics,
        time=time_for_dt_estimate,
        initial_condition=initial_condition,
        target_initial_cfl=spec.target_initial_cfl,
    )
    time = TimeConfig(
        dt=dt,
        steps=spec.steps,
        save_every=max(spec.steps, 1),
        cfl_safety=spec.cfl_safety,
        diffusion_safety=spec.diffusion_safety,
    )
    return SimulationConfig(
        experiment_name=f"stress_validation_2d_{spec.name}",
        grid=grid,
        time=time,
        physics=physics,
        initial_condition=initial_condition,
        output=OutputConfig(
            output_dir=str(output_dir),
            save_plots=False,
            save_snapshots=True,
            log_level="INFO",
        ),
    )


def _dt_for_target_initial_cfl(
    *,
    grid: GridConfig,
    physics: PhysicsConfig,
    time: TimeConfig,
    initial_condition: InitialConditionConfig,
    target_initial_cfl: float,
) -> float:
    if target_initial_cfl <= 0.0 or not np.isfinite(target_initial_cfl):
        raise ValueError("target_initial_cfl must be finite and positive.")
    vorticity = create_initial_vorticity(initial_condition, grid)
    solver = NavierStokesSpectralSolver(grid=grid, physics=physics, time=time)
    state = solver.compute_stability(vorticity)
    cfl_per_unit_dt = state.cfl_number
    if cfl_per_unit_dt <= 0.0 or not np.isfinite(cfl_per_unit_dt):
        raise ValueError("Cannot estimate dt because initial CFL scale is not positive and finite.")
    return float(target_initial_cfl / cfl_per_unit_dt)


def _diffusion_margin(config: SimulationConfig) -> float:
    dx = config.grid.lx / config.grid.nx
    dy = config.grid.ly / config.grid.ny
    diffusion_number = config.physics.viscosity * config.time.dt * (2.0 / dx**2 + 2.0 / dy**2)
    return float(config.time.diffusion_safety - diffusion_number)


def _metrics_summary(metrics: list[dict[str, float]]) -> dict[str, Any]:
    if not metrics:
        return {"samples": 0, "finite_metrics": False}
    energy = np.array([float(item["energy"]) for item in metrics], dtype=float)
    enstrophy = np.array([float(item["enstrophy"]) for item in metrics], dtype=float)
    max_velocity = np.array([float(item["max_velocity"]) for item in metrics], dtype=float)
    cfl = np.array([float(item["cfl"]) for item in metrics], dtype=float)
    flat_values = np.concatenate([energy, enstrophy, max_velocity, cfl])
    finite_metrics = bool(np.all(np.isfinite(flat_values)))
    return {
        "samples": len(metrics),
        "finite_metrics": finite_metrics,
        "initial_energy": float(energy[0]),
        "final_energy": float(energy[-1]),
        "initial_enstrophy": float(enstrophy[0]),
        "final_enstrophy": float(enstrophy[-1]),
        "max_velocity_peak": float(np.max(max_velocity)),
        "cfl_peak": float(np.max(cfl)),
        "cfl_final": float(cfl[-1]),
    }


def _final_spectral_evidence(config: SimulationConfig) -> dict[str, Any]:
    snapshot_path = Path(config.output.output_dir) / "snapshots" / f"vorticity_{config.time.steps:05d}.npy"
    if not snapshot_path.exists():
        return {
            "status": "missing",
            "interpretation": "diagnostic_only_not_hard_gate",
            "artifact": str(snapshot_path),
        }
    vorticity = np.load(snapshot_path)
    solver = NavierStokesSpectralSolver(
        grid=config.grid,
        physics=config.physics,
        time=config.time,
    )
    u, v = solver.velocity_from_vorticity(vorticity)
    diagnostics = compute_velocity_energy_spectrum_2d(u, v, config.grid.lx, config.grid.ly)
    return {
        "status": "available",
        "total_spectral_energy": float(diagnostics["total_spectral_energy"]),
        "high_wavenumber_energy_fraction": float(
            diagnostics["high_wavenumber_energy_fraction"]
        ),
        "max_resolved_wavenumber": float(diagnostics["max_resolved_wavenumber"]),
        "nyquist_wavenumber_estimate": float(diagnostics["nyquist_wavenumber_estimate"]),
        "artifact": str(snapshot_path),
        "interpretation": "diagnostic_only_not_hard_gate",
    }


def _classify_completed_scenario(
    *,
    spec: StressScenarioSpec,
    config: SimulationConfig,
    run_result: dict[str, object],
) -> tuple[str, list[str], dict[str, Any]]:
    warnings: list[str] = []
    metrics = run_result.get("metrics")
    if not isinstance(metrics, list):
        return "failed", ["metrics_missing"], {"samples": 0, "finite_metrics": False}

    summary = _metrics_summary(metrics)
    if not bool(summary["finite_metrics"]):
        return "failed", ["non_finite_metrics_detected"], summary

    validation_report = run_result.get("validation_report")
    if isinstance(validation_report, dict):
        warnings.extend(str(item) for item in validation_report.get("warnings", []))
        validation_status = str(validation_report.get("status", "warn"))
    else:
        validation_status = "warn"
        warnings.append("validation_report_missing")

    cfl_peak = float(summary["cfl_peak"])
    cfl_margin = float(config.time.cfl_safety - cfl_peak)
    diffusion_margin = _diffusion_margin(config)
    if cfl_margin <= 0.0:
        return "failed", warnings + ["cfl_margin_non_positive_after_run"], summary
    if diffusion_margin <= 0.0:
        return "failed", warnings + ["diffusion_margin_non_positive_after_run"], summary
    if cfl_margin < 0.08:
        warnings.append("small_positive_cfl_margin")
    if spec.name in {"near_cfl_limit", "high_amplitude"} and cfl_margin < 0.16:
        warnings.append("stress_condition_close_to_cfl_limit")

    if validation_status == "fail":
        return "failed", warnings, summary
    if validation_status == "warn" or warnings:
        return "warning", warnings, summary
    return "passed", warnings, summary


def _run_single_scenario(spec: StressScenarioSpec, output_dir: Path) -> dict[str, Any]:
    scenario_output_dir = output_dir / spec.name
    config = _build_config(spec, scenario_output_dir)
    try:
        run_result = run_simulation(config, validate=True)
    except Exception as exc:  # noqa: BLE001 - scenario harness records controlled failures.
        message = str(exc)
        is_expected = bool(
            spec.expected_failure_reason and spec.expected_failure_reason in message
        )
        status = "expected_fail_closed" if is_expected else "failed"
        return {
            "name": spec.name,
            "status": status,
            "expected_failure_reason": spec.expected_failure_reason,
            "error": {
                "type": exc.__class__.__name__,
                "message": message,
                "controlled": is_expected,
            },
            "resolved_configuration": asdict(config),
            "warnings": [] if is_expected else ["unexpected_exception"],
            "diagnostic_note": spec.diagnostic_note,
        }

    status, warnings, summary = _classify_completed_scenario(
        spec=spec,
        config=config,
        run_result=run_result,
    )
    spectral_evidence = _final_spectral_evidence(config)
    if spec.name == "spectral_high_k_observation" and spectral_evidence["status"] == "available":
        warnings.append("high_wavenumber_fraction_recorded_as_diagnostic_only")
        if status == "passed":
            status = "warning"

    return {
        "name": spec.name,
        "status": status,
        "expected_failure_reason": spec.expected_failure_reason,
        "metrics_summary": summary,
        "stability_summary": {
            "cfl_limit": float(config.time.cfl_safety),
            "cfl_margin_min": float(config.time.cfl_safety - summary["cfl_peak"]),
            "diffusion_limit": float(config.time.diffusion_safety),
            "diffusion_margin": _diffusion_margin(config),
        },
        "spectral_evidence": spectral_evidence,
        "resolved_configuration": asdict(config),
        "warnings": warnings,
        "artifacts": {
            "output_dir": str(scenario_output_dir),
            "metrics_csv": str(run_result["metrics_csv"]),
            "validation_report_path": str(run_result["validation_report_path"]),
            "resolved_config_path": str(scenario_output_dir / "resolved_config.json"),
        },
        "diagnostic_note": spec.diagnostic_note,
    }


def _multiple_seeds_scenario(output_dir: Path) -> dict[str, Any]:
    seeds = (7, 13, 29)
    subruns: list[dict[str, Any]] = []
    for seed in seeds:
        spec = StressScenarioSpec(
            name=f"multiple_seeds_seed_{seed}",
            seed=seed,
            steps=16,
            target_initial_cfl=0.3,
            diagnostic_note="Deterministic seed sensitivity subrun.",
        )
        subruns.append(_run_single_scenario(spec, output_dir / "multiple_seeds"))

    statuses = [str(item["status"]) for item in subruns]
    warnings = [
        f"{item['name']}:{warning}"
        for item in subruns
        for warning in item.get("warnings", [])
    ]
    completed = [item for item in subruns if "metrics_summary" in item]
    cfl_peaks = [float(item["metrics_summary"]["cfl_peak"]) for item in completed]
    final_energies = [float(item["metrics_summary"]["final_energy"]) for item in completed]

    if any(status == "failed" for status in statuses):
        status = "failed"
    elif any(status == "warning" for status in statuses):
        status = "warning"
    else:
        status = "passed"

    return {
        "name": "multiple_seeds",
        "status": status,
        "subruns": subruns,
        "sensitivity_summary": {
            "seed_count": len(seeds),
            "completed_count": len(completed),
            "cfl_peak_min": float(np.min(cfl_peaks)) if cfl_peaks else None,
            "cfl_peak_max": float(np.max(cfl_peaks)) if cfl_peaks else None,
            "final_energy_min": float(np.min(final_energies)) if final_energies else None,
            "final_energy_max": float(np.max(final_energies)) if final_energies else None,
        },
        "warnings": warnings,
        "diagnostic_note": "Several deterministic seeds are executed to expose sensitivity without making broad statistical claims.",
    }


def _scenario_specs() -> tuple[StressScenarioSpec, ...]:
    return (
        StressScenarioSpec(
            name="baseline_control",
            steps=24,
            target_initial_cfl=0.25,
            diagnostic_note="Nominal deterministic control case; expected to pass.",
        ),
        StressScenarioSpec(
            name="near_cfl_limit",
            steps=12,
            target_initial_cfl=0.72,
            diagnostic_note="Runs close to the configured CFL safety limit with a small positive margin.",
        ),
        StressScenarioSpec(
            name="cfl_violation_expected_fail",
            steps=4,
            target_initial_cfl=0.95,
            expected_failure_reason="CFL violation",
            diagnostic_note="Intentionally violates CFL safety and must fail closed.",
        ),
        StressScenarioSpec(
            name="low_viscosity",
            viscosity=1e-5,
            steps=20,
            target_initial_cfl=0.32,
            diagnostic_note="Lower dissipation case; stability is observed but not promoted to a broad physical claim.",
        ),
        StressScenarioSpec(
            name="high_amplitude",
            amplitude=8.0,
            steps=14,
            target_initial_cfl=0.68,
            diagnostic_note="High-amplitude vorticity stresses velocity reconstruction and CFL handling.",
        ),
        StressScenarioSpec(
            name="coarse_grid",
            nx=12,
            ny=12,
            steps=18,
            target_initial_cfl=0.3,
            diagnostic_note="Low-resolution diagnostic case; produces evidence but not accuracy claims.",
        ),
        StressScenarioSpec(
            name="spectral_high_k_observation",
            smoothing_sigma=0.8,
            steps=18,
            target_initial_cfl=0.35,
            diagnostic_note="Records high-wavenumber energy fraction as diagnostic-only spectral evidence.",
        ),
    )


def run_stress_validation_2d(
    base_output_dir: str = "outputs/benchmarks",
) -> dict[str, Path]:
    output_dir = _base_output_path(base_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    scenarios = [_run_single_scenario(spec, output_dir) for spec in _scenario_specs()]
    scenarios.append(_multiple_seeds_scenario(output_dir))

    status_counts = {status: 0 for status in sorted(SCENARIO_STATUSES)}
    warnings: list[str] = []
    for scenario in scenarios:
        status = str(scenario["status"])
        if status not in SCENARIO_STATUSES:
            status = "failed"
            scenario["status"] = status
            scenario.setdefault("warnings", []).append("unknown_status_mapped_to_failed")
        status_counts[status] += 1
        warnings.extend(f"{scenario['name']}:{item}" for item in scenario.get("warnings", []))

    failed_count = status_counts["failed"]
    non_expected_failures = [
        scenario["name"]
        for scenario in scenarios
        if scenario["status"] == "failed"
    ]
    if failed_count > 0:
        stress_validation_status = "failed"
    elif status_counts["warning"] > 0:
        stress_validation_status = "warning"
    else:
        stress_validation_status = "passed"

    runtime_execution = "failed" if failed_count > 0 else "passed"
    payload = {
        "study_name": STUDY_NAME,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scenarios": scenarios,
        "summary": {
            "scenario_count": len(scenarios),
            "status_counts": status_counts,
            "non_expected_failures": non_expected_failures,
            "expected_fail_closed_count": status_counts["expected_fail_closed"],
            "interpretation": "stress_observation_not_solver_proof",
        },
        "warnings": warnings,
        "acceptance_statuses": {
            "runtime_execution": runtime_execution,
            "stress_validation_status": stress_validation_status,
            "scientific_acceptance": "human_review_required",
            "scientific_acceptance_reasons": [
                "controlled_2d_stress_harness_only",
                "expected_fail_closed_cases_are_not_global_failures",
                "spectral_high_k_observation_is_diagnostic_only",
                "not_a_3d_existence_or_smoothness_proof",
            ],
        },
    }

    summary_path = output_dir / "stress_validation_summary.json"
    summary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {"output_dir": output_dir, "summary_path": summary_path}
