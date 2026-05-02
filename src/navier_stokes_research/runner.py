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


def run_simulation(config: SimulationConfig) -> dict[str, Path]:
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
    )
    vorticity = create_initial_vorticity(config.initial_condition, config.grid)
    metrics: list[dict[str, float]] = []

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
    if config.output.save_plots:
        save_metric_evolution(metrics, plots_dir / "metric_evolution.png")

    LOGGER.info("Completed experiment '%s'", config.experiment_name)
    return {
        "output_dir": output_dir,
        "metrics_csv": metrics_path,
        "plots_dir": plots_dir,
        "snapshots_dir": snapshots_dir,
    }
