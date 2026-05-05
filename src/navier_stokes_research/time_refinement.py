from __future__ import annotations

import json
import math
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from navier_stokes_research.config import (
    GridConfig,
    InitialConditionConfig,
    OutputConfig,
    PhysicsConfig,
    SimulationConfig,
    TimeConfig,
)
from navier_stokes_research.runner import run_simulation

STUDY_NAME = "time_refinement_2d"
FINAL_TIME = 0.24
BASE_DT = 0.003
BASE_STEPS = 80
GRID_SIZE = 32
VISCOSITY = 0.001
SEED = 2026
REL_DIFF_SMALL_THRESHOLD = 0.05
REL_DIFF_REASONABLE_THRESHOLD = 0.2


def _safe_relative_difference(reference: float, candidate: float, epsilon: float = 1e-12) -> float:
    denominator = max(abs(reference), epsilon)
    return abs(candidate - reference) / denominator


def _is_finite_run(run_payload: dict[str, Any]) -> bool:
    numeric_values = (
        run_payload["final_energy"],
        run_payload["final_enstrophy"],
        run_payload["final_max_velocity"],
        run_payload["cfl_peak"],
    )
    return all(math.isfinite(float(value)) for value in numeric_values)


def _build_config(*, dt: float, steps: int, output_dir: Path, level_name: str) -> SimulationConfig:
    return SimulationConfig(
        experiment_name=f"time_refinement_2d_{level_name}",
        grid=GridConfig(nx=GRID_SIZE, ny=GRID_SIZE, lx=6.283185307179586, ly=6.283185307179586),
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


def _run_level(level_name: str, dt: float, steps: int, base_output_dir: Path) -> dict[str, Any]:
    run_dir = base_output_dir / level_name
    config = _build_config(dt=dt, steps=steps, output_dir=run_dir, level_name=level_name)
    run_result = run_simulation(config, validate=True)
    metrics = run_result.get("metrics")
    validation_report = run_result.get("validation_report")
    if not isinstance(metrics, list) or not metrics:
        raise RuntimeError(f"Missing metrics for time-refinement level: {level_name}")
    if not isinstance(validation_report, dict):
        raise RuntimeError(f"Missing validation report for time-refinement level: {level_name}")

    final_metrics = metrics[-1]
    cfl_peak = max(float(item["cfl"]) for item in metrics)
    validation_status = str(validation_report.get("status", "fail"))
    warnings = [str(item) for item in validation_report.get("warnings", [])]
    level_status = "passed"
    if validation_status == "warn":
        level_status = "warning"
    elif validation_status != "pass":
        level_status = "failed"

    payload = {
        "name": level_name,
        "status": level_status,
        "dt": float(dt),
        "steps": int(steps),
        "final_time": float(steps * dt),
        "final_energy": float(final_metrics["energy"]),
        "final_enstrophy": float(final_metrics["enstrophy"]),
        "final_max_velocity": float(final_metrics["max_velocity"]),
        "cfl_peak": float(cfl_peak),
        "validation_status": validation_status,
        "warnings": warnings,
        "artifacts": {
            "output_dir": str(run_result["output_dir"]),
            "metrics_csv": str(run_result["metrics_csv"]),
            "validation_report_path": str(run_result["validation_report_path"]),
        },
        "resolved_configuration": asdict(config),
    }
    if not _is_finite_run(payload):
        payload["status"] = "failed"
        payload["warnings"].append("non_finite_metrics_detected")
    return payload


def _assess_comparison(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    return {
        "coarse_level": previous["name"],
        "fine_level": current["name"],
        "energy_relative_difference": _safe_relative_difference(
            float(previous["final_energy"]), float(current["final_energy"])
        ),
        "enstrophy_relative_difference": _safe_relative_difference(
            float(previous["final_enstrophy"]), float(current["final_enstrophy"])
        ),
        "max_velocity_relative_difference": _safe_relative_difference(
            float(previous["final_max_velocity"]), float(current["final_max_velocity"])
        ),
    }


def run_time_refinement_validation_2d(
    base_output_dir: str = "outputs/benchmarks",
) -> dict[str, Path]:
    study_dir = Path(base_output_dir) / STUDY_NAME
    study_dir.mkdir(parents=True, exist_ok=True)

    dt_levels = [
        ("dt_base", BASE_DT, BASE_STEPS),
        ("dt_half", BASE_DT / 2.0, BASE_STEPS * 2),
        ("dt_quarter", BASE_DT / 4.0, BASE_STEPS * 4),
    ]

    runs: list[dict[str, Any]] = []
    unexpected_failures: list[str] = []
    warnings: list[str] = []
    runtime_execution = "passed"

    for level_name, dt, steps in dt_levels:
        try:
            run_payload = _run_level(level_name=level_name, dt=dt, steps=steps, base_output_dir=study_dir)
        except Exception as exc:
            runtime_execution = "failed"
            unexpected_failures.append(level_name)
            runs.append(
                {
                    "name": level_name,
                    "status": "failed",
                    "dt": float(dt),
                    "steps": int(steps),
                    "final_time": float(steps * dt),
                    "final_energy": None,
                    "final_enstrophy": None,
                    "final_max_velocity": None,
                    "cfl_peak": None,
                    "validation_status": "failed_exception",
                    "warnings": [f"unexpected_exception:{type(exc).__name__}"],
                }
            )
            continue

        runs.append(run_payload)
        if run_payload["status"] == "failed":
            unexpected_failures.append(level_name)
        warnings.extend(f"{level_name}:{item}" for item in run_payload["warnings"])

    comparisons: list[dict[str, Any]] = []
    if len(runs) == 3 and all(run["status"] != "failed" for run in runs):
        comparisons.append(_assess_comparison(runs[0], runs[1]))
        comparisons.append(_assess_comparison(runs[1], runs[2]))

    small_or_decreasing = False
    finite_comparisons = all(
        math.isfinite(float(item[key]))
        for item in comparisons
        for key in (
            "energy_relative_difference",
            "enstrophy_relative_difference",
            "max_velocity_relative_difference",
        )
    )
    if len(comparisons) == 2 and finite_comparisons:
        first = comparisons[0]
        second = comparisons[1]
        decreasing_each_metric = (
            second["energy_relative_difference"] <= first["energy_relative_difference"]
            and second["enstrophy_relative_difference"] <= first["enstrophy_relative_difference"]
            and second["max_velocity_relative_difference"] <= first["max_velocity_relative_difference"]
        )
        small_each_metric = (
            second["energy_relative_difference"] <= REL_DIFF_SMALL_THRESHOLD
            and second["enstrophy_relative_difference"] <= REL_DIFF_SMALL_THRESHOLD
            and second["max_velocity_relative_difference"] <= REL_DIFF_SMALL_THRESHOLD
        )
        small_or_decreasing = decreasing_each_metric or small_each_metric

    if runtime_execution == "failed" or unexpected_failures:
        time_refinement_status = "failed"
    elif len(comparisons) != 2 or not finite_comparisons:
        time_refinement_status = "failed"
        warnings.append("comparisons_missing_or_non_finite")
    elif small_or_decreasing:
        time_refinement_status = "passed"
    else:
        all_reasonable = all(
            item["energy_relative_difference"] <= REL_DIFF_REASONABLE_THRESHOLD
            and item["enstrophy_relative_difference"] <= REL_DIFF_REASONABLE_THRESHOLD
            and item["max_velocity_relative_difference"] <= REL_DIFF_REASONABLE_THRESHOLD
            for item in comparisons
        )
        time_refinement_status = "warning" if all_reasonable else "failed"
        if time_refinement_status == "warning":
            warnings.append("relative_differences_not_decreasing_but_reasonable")
        else:
            warnings.append("relative_differences_large_or_unstable")

    payload = {
        "study_name": STUDY_NAME,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "domain_scope": "2d_periodic_only",
        "dt_levels": runs,
        "comparisons": comparisons,
        "summary": {
            "runtime_execution": runtime_execution,
            "time_refinement_status": time_refinement_status,
            "unexpected_failures": unexpected_failures,
        },
        "scientific_acceptance": "human_review_required",
        "scientific_acceptance_reasons": [
            "controlled_2d_periodic_time_refinement_only",
            "diagnostic_numerical_evidence_not_formal_proof",
            "not_a_3d_existence_or_smoothness_proof",
        ],
        "warnings": warnings,
    }

    summary_path = study_dir / "time_refinement_summary.json"
    summary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {"output_dir": study_dir, "summary_path": summary_path}
