from __future__ import annotations

import csv
import json
import logging
from pathlib import Path

import numpy as np

from navier_stokes_research.config import SimulationConfig
from navier_stokes_research.initial_conditions import create_initial_vorticity
from navier_stokes_research.metrics import summarize_state
from navier_stokes_research.solver import NavierStokesSpectralSolver
from navier_stokes_research.validation import (
    evaluate_validation,
    summarize_validation_for_log,
    write_validation_report,
)
from navier_stokes_research.visualization import save_heatmap, save_metric_evolution

LOGGER = logging.getLogger(__name__)


def _write_metrics_csv(metrics: list[dict[str, float]], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["step", "time", "energy", "enstrophy", "max_velocity", "cfl"],
        )
        writer.writeheader()
        writer.writerows(metrics)


def _write_forcing_metrics_csv(metrics: list[dict[str, float]], path: Path) -> None:
    if not metrics:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(metrics[0].keys()))
        writer.writeheader()
        writer.writerows(metrics)


def _summarize_forcing_budget(
    *,
    step: int,
    time_value: float,
    solver: NavierStokesSpectralSolver,
    vorticity: np.ndarray,
    energy: float,
    enstrophy: float,
) -> dict[str, float]:
    streamfunction = solver.solve_streamfunction(vorticity)
    cell_area = solver.dx * solver.dy
    epsilon_in = float(np.sum(streamfunction * solver.forcing_field) * cell_area)
    epsilon_viscous = float(2.0 * solver.physics.viscosity * enstrophy)
    epsilon_drag = float(2.0 * solver.forcing.ekman_drag * energy)
    epsilon_dissipation = epsilon_viscous + epsilon_drag
    denominator = max(abs(epsilon_in), 1.0e-14)
    residual = abs(epsilon_in - epsilon_dissipation)
    return {
        "step": float(step),
        "time": float(time_value),
        "epsilon_in": epsilon_in,
        "epsilon_viscous": epsilon_viscous,
        "epsilon_drag": epsilon_drag,
        "epsilon_dissipation": epsilon_dissipation,
        "energy_balance_residual": residual,
        "energy_balance_residual_normalized": float(residual / denominator),
        "energy": float(energy),
        "enstrophy": float(enstrophy),
    }


def run_simulation(config: SimulationConfig, validate: bool = False) -> dict[str, object]:
    output_dir = Path(config.output.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshots_dir = output_dir / "snapshots"
    plots_dir = output_dir / "plots"
    if config.output.save_snapshots:
        snapshots_dir.mkdir(parents=True, exist_ok=True)
    if config.output.save_plots:
        plots_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "resolved_config.json").write_text(
        json.dumps(config.to_dict(), indent=2),
        encoding="utf-8",
    )

    solver = NavierStokesSpectralSolver(
        grid=config.grid,
        physics=config.physics,
        time=config.time,
        forcing=config.forcing,
    )
    vorticity = create_initial_vorticity(config.initial_condition, config.grid)
    metrics: list[dict[str, float]] = []
    forcing_metrics: list[dict[str, float]] = []

    LOGGER.info("Starting experiment '%s'", config.experiment_name)
    stability = solver.ensure_stability(vorticity)

    for step in range(config.time.steps + 1):
        u, v = solver.velocity_from_vorticity(vorticity)
        summary = summarize_state(
            step=step,
            time_value=step * config.time.dt,
            vorticity=vorticity,
            u=u,
            v=v,
            dx=solver.dx,
            dy=solver.dy,
            cfl_number=stability.cfl_number,
        )
        metrics.append(summary)
        if config.forcing.enabled:
            forcing_metrics.append(
                _summarize_forcing_budget(
                    step=step,
                    time_value=step * config.time.dt,
                    solver=solver,
                    vorticity=vorticity,
                    energy=summary["energy"],
                    enstrophy=summary["enstrophy"],
                )
            )

        if step % config.time.save_every == 0:
            LOGGER.info(
                "step=%s time=%.4f energy=%.6f enstrophy=%.6f max_velocity=%.6f cfl=%.6f",
                step,
                summary["time"],
                summary["energy"],
                summary["enstrophy"],
                summary["max_velocity"],
                summary["cfl"],
            )
            if config.output.save_snapshots:
                np.save(snapshots_dir / f"vorticity_{step:05d}.npy", vorticity)
            if config.output.save_plots:
                save_heatmap(
                    field=vorticity,
                    path=plots_dir / f"vorticity_{step:05d}.png",
                    title=f"Vorticity at step {step}",
                    colorbar_label="omega",
                )

        if step == config.time.steps:
            break

        vorticity, stability = solver.step(vorticity)

    metrics_path = output_dir / "metrics.csv"
    _write_metrics_csv(metrics, metrics_path)
    forcing_metrics_path = output_dir / "forcing_metrics.csv"
    if forcing_metrics:
        _write_forcing_metrics_csv(forcing_metrics, forcing_metrics_path)
    if config.output.save_plots:
        save_metric_evolution(metrics, plots_dir / "metric_evolution.png")

    result: dict[str, object] = {
        "output_dir": output_dir,
        "metrics_csv": metrics_path,
        "plots_dir": plots_dir,
        "snapshots_dir": snapshots_dir,
        "metrics": metrics,
    }
    if forcing_metrics:
        result["forcing_metrics"] = forcing_metrics
        result["forcing_metrics_csv"] = forcing_metrics_path
    if validate:
        report = evaluate_validation(metrics, config)
        report_path = output_dir / "validation_report.json"
        write_validation_report(report_path, report)
        LOGGER.info(summarize_validation_for_log(report))
        result["validation_report"] = report
        result["validation_report_path"] = report_path

    LOGGER.info("Completed experiment '%s'", config.experiment_name)
    return result
