from __future__ import annotations

import csv
import json
import math
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from navier_stokes_research.config import (
    GridConfig,
    InitialConditionConfig,
    OutputConfig,
    PhysicsConfig,
    SimulationConfig,
    TimeConfig,
)
from navier_stokes_research.interpretation import (
    interpret_convergence_quality,
    write_quality_report,
)
from navier_stokes_research.reporting import generate_convergence_report, generate_reports_index
from navier_stokes_research.runner import run_simulation


DEFAULT_RESOLUTIONS = (32, 64)
EXTENDED_RESOLUTIONS = (32, 64, 128, 256, 512)
DEFAULT_BASE_RESOLUTION = 64
DEFAULT_BASE_DT = 0.0015
DEFAULT_FINAL_TIME = 0.24
DEFAULT_VISCOSITY = 0.001
DEFAULT_SEED = 2026


def _relative_difference(reference: float, candidate: float, epsilon: float = 1e-12) -> float:
    denominator = max(abs(reference), epsilon)
    return abs(candidate - reference) / denominator


def _safe_self_convergence_order(
    delta_coarse: float,
    delta_fine: float,
    refinement_ratio: float,
    epsilon: float = 1e-14,
) -> float | None:
    """Estimate self-convergence order from three consecutive refinements.

    Uses p = log(delta_coarse / delta_fine) / log(r), where deltas are
    absolute differences between consecutive scalar observables.
    This is diagnostic evidence, not a formal proof of convergence.
    """
    if refinement_ratio <= 1.0:
        return None
    if delta_coarse <= epsilon or delta_fine <= epsilon:
        return None
    return math.log(delta_coarse / delta_fine) / math.log(refinement_ratio)


def _estimate_self_convergence_orders(
    rows: list[dict[str, float | int | str | None]],
) -> list[dict[str, float | int | str | None]]:
    estimates: list[dict[str, float | int | str | None]] = []
    metrics = (
        ("energy", "final_energy"),
        ("enstrophy", "final_enstrophy"),
        ("max_velocity", "final_max_velocity"),
    )

    for idx in range(2, len(rows)):
        coarse = rows[idx - 2]
        medium = rows[idx - 1]
        fine = rows[idx]

        n0 = int(coarse["resolution"])
        n1 = int(medium["resolution"])
        n2 = int(fine["resolution"])

        ratio_01 = n1 / n0
        ratio_12 = n2 / n1
        uniform_ratio = abs(ratio_01 - ratio_12) <= 1e-12

        estimate: dict[str, float | int | str | None] = {
            "coarse_resolution": n0,
            "medium_resolution": n1,
            "fine_resolution": n2,
            "refinement_ratio": ratio_12 if uniform_ratio else None,
            "method": "self_convergence_order_log_delta_ratio",
            "note": (
                "diagnostic_only_not_formal_proof"
                if uniform_ratio
                else "non_uniform_refinement_ratio"
            ),
        }

        for metric_name, field_name in metrics:
            delta_coarse = abs(float(medium[field_name]) - float(coarse[field_name]))
            delta_fine = abs(float(fine[field_name]) - float(medium[field_name]))
            estimate[f"{metric_name}_delta_coarse"] = delta_coarse
            estimate[f"{metric_name}_delta_fine"] = delta_fine
            estimate[f"{metric_name}_order"] = (
                _safe_self_convergence_order(delta_coarse, delta_fine, ratio_12)
                if uniform_ratio
                else None
            )

        estimates.append(estimate)

    return estimates


def _build_convergence_config(
    *,
    resolution: int,
    dt: float,
    steps: int,
    output_dir: str,
    viscosity: float,
    seed: int,
    save_plots: bool,
) -> SimulationConfig:
    return SimulationConfig(
        experiment_name=f"convergence_n{resolution}",
        grid=GridConfig(nx=resolution, ny=resolution, lx=6.283185307179586, ly=6.283185307179586),
        time=TimeConfig(
            dt=dt,
            steps=steps,
            save_every=max(1, steps // 4),
            cfl_safety=0.8,
            diffusion_safety=0.5,
        ),
        physics=PhysicsConfig(viscosity=viscosity),
        initial_condition=InitialConditionConfig(
            kind="vortices",
            amplitude=1.0,
            seed=seed,
            vortex_radius=0.35,
            vortex_strength=8.0,
            vortex_distance=1.2,
        ),
        output=OutputConfig(
            output_dir=output_dir,
            save_plots=save_plots,
            save_snapshots=False,
            log_level="INFO",
        ),
    )


def _write_convergence_metrics_csv(rows: list[dict[str, float | int | str | None]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "resolution",
                "dt",
                "steps",
                "final_time",
                "final_energy",
                "final_enstrophy",
                "final_max_velocity",
                "cfl_peak",
                "validation_status",
                "rel_diff_energy_vs_prev",
                "rel_diff_enstrophy_vs_prev",
                "rel_diff_max_velocity_vs_prev",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def _save_comparison_plot(rows: list[dict[str, float | int | str | None]], path: Path) -> None:
    resolutions = [int(row["resolution"]) for row in rows]
    energy = [float(row["final_energy"]) for row in rows]
    enstrophy = [float(row["final_enstrophy"]) for row in rows]
    max_velocity = [float(row["final_max_velocity"]) for row in rows]

    fig, axes = plt.subplots(3, 1, figsize=(8, 9), constrained_layout=True)
    axes[0].plot(resolutions, energy, marker="o", color="#0f766e")
    axes[0].set_title("Final Energy vs Resolution")
    axes[1].plot(resolutions, enstrophy, marker="o", color="#b45309")
    axes[1].set_title("Final Enstrophy vs Resolution")
    axes[2].plot(resolutions, max_velocity, marker="o", color="#1d4ed8")
    axes[2].set_title("Final Max Velocity vs Resolution")
    for axis in axes:
        axis.set_xlabel("Grid Resolution N (NxN)")
        axis.grid(alpha=0.25)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def run_convergence_study(
    *,
    base_output_dir: str = "outputs/convergence",
    study_name: str = "baseline_resolution_study",
    resolutions: tuple[int, ...] | None = None,
    extended: bool = False,
    base_resolution: int = DEFAULT_BASE_RESOLUTION,
    base_dt: float = DEFAULT_BASE_DT,
    final_time: float = DEFAULT_FINAL_TIME,
    viscosity: float = DEFAULT_VISCOSITY,
    seed: int = DEFAULT_SEED,
    save_plots: bool = True,
) -> dict[str, Path]:
    selected_resolutions = resolutions or (EXTENDED_RESOLUTIONS if extended else DEFAULT_RESOLUTIONS)
    if len(selected_resolutions) < 2:
        raise ValueError("At least two resolutions are required for convergence comparison.")
    if any(value <= 0 for value in selected_resolutions):
        raise ValueError("All resolutions must be positive integers.")
    sorted_resolutions = tuple(sorted(set(selected_resolutions)))

    study_dir = Path(base_output_dir) / study_name
    study_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, float | int | str | None]] = []
    runs: list[dict[str, object]] = []
    warnings: list[str] = []
    previous: dict[str, float] | None = None

    for resolution in sorted_resolutions:
        dt = base_dt * (base_resolution / resolution)
        steps = max(1, int(round(final_time / dt)))
        physical_horizon = steps * dt
        run_dir = study_dir / f"n{resolution}"
        config = _build_convergence_config(
            resolution=resolution,
            dt=dt,
            steps=steps,
            output_dir=str(run_dir),
            viscosity=viscosity,
            seed=seed,
            save_plots=save_plots,
        )
        run_result = run_simulation(config, validate=True)
        validation_report = run_result.get("validation_report")
        if not isinstance(validation_report, dict):
            raise RuntimeError(f"Validation report missing for resolution {resolution}.")

        metrics = run_result.get("metrics")
        if not isinstance(metrics, list) or not metrics:
            raise RuntimeError(f"Metrics missing for resolution {resolution}.")

        final_metrics = metrics[-1]
        cfl_peak = max(float(entry["cfl"]) for entry in metrics)

        rel_energy = None
        rel_enstrophy = None
        rel_max_velocity = None
        if previous is not None:
            rel_energy = _relative_difference(previous["final_energy"], float(final_metrics["energy"]))
            rel_enstrophy = _relative_difference(previous["final_enstrophy"], float(final_metrics["enstrophy"]))
            rel_max_velocity = _relative_difference(
                previous["final_max_velocity"],
                float(final_metrics["max_velocity"]),
            )

        row = {
            "resolution": resolution,
            "dt": dt,
            "steps": steps,
            "final_time": physical_horizon,
            "final_energy": float(final_metrics["energy"]),
            "final_enstrophy": float(final_metrics["enstrophy"]),
            "final_max_velocity": float(final_metrics["max_velocity"]),
            "cfl_peak": cfl_peak,
            "validation_status": str(validation_report["status"]),
            "rel_diff_energy_vs_prev": rel_energy,
            "rel_diff_enstrophy_vs_prev": rel_enstrophy,
            "rel_diff_max_velocity_vs_prev": rel_max_velocity,
        }
        rows.append(row)
        previous = {
            "final_energy": float(final_metrics["energy"]),
            "final_enstrophy": float(final_metrics["enstrophy"]),
            "final_max_velocity": float(final_metrics["max_velocity"]),
        }

        if validation_report["status"] != "pass":
            warnings.append(f"resolution_n{resolution}_validation_warn")
        runs.append(
            {
                "resolution": resolution,
                "config": asdict(config),
                "final_metrics": final_metrics,
                "cfl_peak": cfl_peak,
                "validation_status": validation_report["status"],
                "validation_warnings": validation_report["warnings"],
                "artifacts": {
                    **{
                        key: str(value)
                        for key, value in run_result.items()
                        if key.endswith("_path") or key.endswith("_dir")
                    },
                    "metrics_csv": str(run_result["metrics_csv"]),
                },
            }
        )

    csv_path = study_dir / "convergence_metrics.csv"
    _write_convergence_metrics_csv(rows, csv_path)
    plot_path = study_dir / "convergence_comparison.png"
    _save_comparison_plot(rows, plot_path)

    estimated_orders = _estimate_self_convergence_orders(rows)
    runtime_execution_status = (
        "passed"
        if not warnings and all(run.get("validation_status") == "pass" for run in runs)
        else "warning"
    )

    summary = {
        "study_name": study_name,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "method_notes": {
            "relative_difference_epsilon": 1e-12,
            "dt_scaling_rule": "dt = base_dt * (base_resolution / resolution)",
            "physical_horizon_rule": "steps = round(final_time / dt)",
        },
        "inputs": {
            "extended": extended,
            "resolutions": list(sorted_resolutions),
            "base_resolution": base_resolution,
            "base_dt": base_dt,
            "target_final_time": final_time,
            "viscosity": viscosity,
            "seed": seed,
            "initial_condition_kind": "vortices",
        },
        "runs": runs,
        "relative_differences_consecutive": [
            {
                "from_resolution": rows[idx - 1]["resolution"],
                "to_resolution": rows[idx]["resolution"],
                "energy": rows[idx]["rel_diff_energy_vs_prev"],
                "enstrophy": rows[idx]["rel_diff_enstrophy_vs_prev"],
                "max_velocity": rows[idx]["rel_diff_max_velocity_vs_prev"],
            }
            for idx in range(1, len(rows))
        ],
        "estimated_self_convergence_orders": estimated_orders,
        "warnings": warnings,
        "acceptance_statuses": {
            "runtime_execution": runtime_execution_status,
            "heuristic_consistency": "pending_quality_interpretation",
            "scientific_acceptance": "human_review_required",
            "scientific_acceptance_reasons": [
                "baseline_2d_only",
                "no_exact_reference_solution_used_in_this_study",
                "self_convergence_orders_are_diagnostic_not_formal_proof",
            ],
        },
        "artifacts": {
            "study_dir": str(study_dir),
            "convergence_metrics_csv": str(csv_path),
            "comparison_plot_png": str(plot_path),
        },
    }
    summary_path = study_dir / "convergence_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    quality = interpret_convergence_quality(summary=summary, output_dir=study_dir)
    quality_path = study_dir / "convergence_quality.json"
    write_quality_report(quality_path, quality)
    summary["quality_interpretation"] = quality
    summary["acceptance_statuses"]["heuristic_consistency"] = str(quality.get("status", "unknown"))
    summary["artifacts"]["convergence_quality_json"] = str(quality_path)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    report_path = generate_convergence_report(study_dir, language="es")
    reports_index_path = generate_reports_index()

    return {
        "study_dir": study_dir,
        "convergence_summary_path": summary_path,
        "convergence_metrics_csv_path": csv_path,
        "comparison_plot_path": plot_path,
        "convergence_quality_path": quality_path,
        "convergence_report_path": report_path,
        "reports_index_path": reports_index_path,
    }
