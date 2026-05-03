from __future__ import annotations

import csv
import json
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
from navier_stokes_research.runner import run_simulation


DEFAULT_RESOLUTIONS = (32, 64)
DEFAULT_BASE_RESOLUTION = 64
DEFAULT_BASE_DT = 0.0015
DEFAULT_FINAL_TIME = 0.24
DEFAULT_VISCOSITY = 0.001
DEFAULT_SEED = 2026


def _relative_difference(reference: float, candidate: float, epsilon: float = 1e-12) -> float:
    denominator = max(abs(reference), epsilon)
    return abs(candidate - reference) / denominator


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
            kind="random",
            amplitude=1.0,
            smoothing_sigma=6.0,
            seed=seed,
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
    resolutions: tuple[int, ...] = DEFAULT_RESOLUTIONS,
    base_resolution: int = DEFAULT_BASE_RESOLUTION,
    base_dt: float = DEFAULT_BASE_DT,
    final_time: float = DEFAULT_FINAL_TIME,
    viscosity: float = DEFAULT_VISCOSITY,
    seed: int = DEFAULT_SEED,
    save_plots: bool = True,
) -> dict[str, Path]:
    if len(resolutions) < 2:
        raise ValueError("At least two resolutions are required for convergence comparison.")
    if any(value <= 0 for value in resolutions):
        raise ValueError("All resolutions must be positive integers.")
    sorted_resolutions = tuple(sorted(set(resolutions)))

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
                    key: str(value)
                    for key, value in run_result.items()
                    if key.endswith("_path") or key.endswith("_dir")
                },
            }
        )

    csv_path = study_dir / "convergence_metrics.csv"
    _write_convergence_metrics_csv(rows, csv_path)
    plot_path = study_dir / "convergence_comparison.png"
    _save_comparison_plot(rows, plot_path)

    summary = {
        "study_name": study_name,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "method_notes": {
            "relative_difference_epsilon": 1e-12,
            "dt_scaling_rule": "dt = base_dt * (base_resolution / resolution)",
            "physical_horizon_rule": "steps = round(final_time / dt)",
        },
        "inputs": {
            "resolutions": list(sorted_resolutions),
            "base_resolution": base_resolution,
            "base_dt": base_dt,
            "target_final_time": final_time,
            "viscosity": viscosity,
            "seed": seed,
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
        "warnings": warnings,
        "artifacts": {
            "study_dir": str(study_dir),
            "convergence_metrics_csv": str(csv_path),
            "comparison_plot_png": str(plot_path),
        },
    }
    summary_path = study_dir / "convergence_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return {
        "study_dir": study_dir,
        "convergence_summary_path": summary_path,
        "convergence_metrics_csv_path": csv_path,
        "comparison_plot_path": plot_path,
    }

