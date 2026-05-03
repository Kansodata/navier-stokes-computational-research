from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from navier_stokes_research.config import (
    GridConfig,
    InitialConditionConfig,
    OutputConfig,
    PhysicsConfig,
    SimulationConfig,
    TimeConfig,
)
from navier_stokes_research.reporting import generate_benchmark_report
from navier_stokes_research.runner import run_simulation


def build_benchmark_config(base_output_dir: str = "outputs/benchmarks") -> SimulationConfig:
    output_dir = f"{base_output_dir}/baseline_2d_incompressible"
    return SimulationConfig(
        experiment_name="benchmark_baseline_2d_incompressible",
        grid=GridConfig(nx=64, ny=64, lx=6.283185307179586, ly=6.283185307179586),
        time=TimeConfig(
            dt=0.0015,
            steps=160,
            save_every=40,
            cfl_safety=0.8,
            diffusion_safety=0.5,
        ),
        physics=PhysicsConfig(viscosity=0.001),
        initial_condition=InitialConditionConfig(
            kind="random",
            amplitude=1.0,
            smoothing_sigma=6.0,
            seed=2026,
        ),
        output=OutputConfig(
            output_dir=output_dir,
            save_plots=True,
            save_snapshots=False,
            log_level="INFO",
        ),
    )


def run_benchmark(base_output_dir: str = "outputs/benchmarks") -> dict[str, Path]:
    config = build_benchmark_config(base_output_dir=base_output_dir)
    run_result = run_simulation(config, validate=True)
    metrics = run_result["metrics"][-1]
    validation_report = run_result["validation_report"]

    summary = {
        "config": asdict(config),
        "final_metrics": metrics,
        "validation_status": validation_report["status"],
        "warnings": validation_report["warnings"],
        "artifacts": {
            key: str(value)
            for key, value in run_result.items()
            if key.endswith("_path") or key.endswith("_dir")
        },
    }

    summary_path = Path(config.output.output_dir) / "benchmark_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    run_result["benchmark_summary_path"] = summary_path
    run_result["benchmark_report_path"] = generate_benchmark_report(config.output.output_dir)
    return run_result
