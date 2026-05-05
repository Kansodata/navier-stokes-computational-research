from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

from navier_stokes_research.config import SimulationConfig


def load_metrics_csv(path: str | Path) -> list[dict[str, float]]:
    metrics_path = Path(path)
    with metrics_path.open("r", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    metrics: list[dict[str, float]] = []
    for row in rows:
        metrics.append(
            {
                "step": float(row["step"]),
                "time": float(row["time"]),
                "energy": float(row["energy"]),
                "enstrophy": float(row["enstrophy"]),
                "max_velocity": float(row["max_velocity"]),
                "cfl": float(row["cfl"]),
            }
        )
    return metrics


def _trend_ratio(series: np.ndarray) -> float:
    start = float(series[0])
    end = float(series[-1])
    if abs(start) < 1e-14:
        return 0.0 if abs(end) < 1e-14 else np.inf
    return end / start


def evaluate_validation(
    metrics: list[dict[str, float]],
    config: SimulationConfig,
    incompressibility_residual_max: float | None = None,
) -> dict[str, Any]:
    if not metrics:
        raise ValueError("Cannot validate empty metrics history.")

    energy = np.array([item["energy"] for item in metrics], dtype=float)
    enstrophy = np.array([item["enstrophy"] for item in metrics], dtype=float)
    max_velocity = np.array([item["max_velocity"] for item in metrics], dtype=float)
    cfl = np.array([item["cfl"] for item in metrics], dtype=float)

    flat_values = np.concatenate([energy, enstrophy, max_velocity, cfl])
    finite_ok = bool(np.all(np.isfinite(flat_values)))

    energy_ratio = _trend_ratio(energy)
    enstrophy_ratio = _trend_ratio(enstrophy)
    max_velocity_growth = float(max_velocity[-1] - max_velocity[0])
    max_velocity_growth_limit = float(max(1.0, 2.0 * float(max_velocity[0])))
    cfl_peak = float(np.max(cfl))
    cfl_margin_min = float(config.time.cfl_safety - cfl_peak)
    diffusion_number = float(
        config.physics.viscosity
        * config.time.dt
        * (
            2.0 / (config.grid.lx / config.grid.nx) ** 2
            + 2.0 / (config.grid.ly / config.grid.ny) ** 2
        )
    )
    diffusion_margin = float(config.time.diffusion_safety - diffusion_number)

    warnings: list[str] = []
    if not finite_ok:
        warnings.append("non_finite_metrics_detected")
    if cfl_margin_min <= 0.0:
        warnings.append("cfl_margin_non_positive")
    if diffusion_margin <= 0.0:
        warnings.append("diffusion_margin_non_positive")
    if energy_ratio > 1.10:
        warnings.append("energy_growth_above_10pct")
    if enstrophy_ratio > 1.10:
        warnings.append("enstrophy_growth_above_10pct")

    checks = {
        "nan_inf_detection": {
            "ok": finite_ok,
            "details": "All diagnostic time-series are finite.",
        },
        "kinetic_energy_trend": {
            "ok": bool(finite_ok and energy_ratio <= 1.10),
            "start": float(energy[0]),
            "end": float(energy[-1]),
            "ratio": float(energy_ratio),
        },
        "enstrophy_trend": {
            "ok": bool(finite_ok and enstrophy_ratio <= 1.10),
            "start": float(enstrophy[0]),
            "end": float(enstrophy[-1]),
            "ratio": float(enstrophy_ratio),
        },
        "max_velocity_growth": {
            "ok": bool(finite_ok and max_velocity_growth <= max_velocity_growth_limit),
            "start": float(max_velocity[0]),
            "end": float(max_velocity[-1]),
            "growth": max_velocity_growth,
        },
        "cfl_margin": {
            "ok": bool(cfl_margin_min > 0.0),
            "cfl_peak": cfl_peak,
            "cfl_limit": float(config.time.cfl_safety),
            "margin_min": cfl_margin_min,
        },
        "diffusion_margin": {
            "ok": bool(diffusion_margin > 0.0),
            "diffusion_number": diffusion_number,
            "diffusion_limit": float(config.time.diffusion_safety),
            "margin": diffusion_margin,
        },
    }

    if incompressibility_residual_max is not None:
        checks["incompressibility_residual"] = {
            "ok": bool(np.isfinite(incompressibility_residual_max)),
            "max_residual": float(incompressibility_residual_max),
        }

    status = "pass" if all(bool(item["ok"]) for item in checks.values()) else "warn"
    return {
        "status": status,
        "warnings": warnings,
        "checks": checks,
        "final_metrics": metrics[-1],
        "sample_count": len(metrics),
    }


def summarize_validation_for_log(report: dict[str, Any]) -> str:
    return (
        f"validation_status={report['status']} "
        f"warnings={len(report['warnings'])} "
        f"energy_ratio={report['checks']['kinetic_energy_trend']['ratio']:.6f} "
        f"enstrophy_ratio={report['checks']['enstrophy_trend']['ratio']:.6f} "
        f"cfl_margin_min={report['checks']['cfl_margin']['margin_min']:.6f} "
        f"diffusion_margin={report['checks']['diffusion_margin']['margin']:.6f}"
    )


def write_validation_report(path: str | Path, report: dict[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
