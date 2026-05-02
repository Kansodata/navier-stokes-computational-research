from __future__ import annotations

import numpy as np


def compute_energy(u: np.ndarray, v: np.ndarray, dx: float, dy: float) -> float:
    return float(0.5 * np.sum(u**2 + v**2) * dx * dy)


def compute_enstrophy(vorticity: np.ndarray, dx: float, dy: float) -> float:
    return float(0.5 * np.sum(vorticity**2) * dx * dy)


def compute_max_velocity(u: np.ndarray, v: np.ndarray) -> float:
    return float(np.max(np.sqrt(u**2 + v**2)))


def summarize_state(
    *,
    step: int,
    time_value: float,
    vorticity: np.ndarray,
    u: np.ndarray,
    v: np.ndarray,
    dx: float,
    dy: float,
    cfl_number: float,
) -> dict[str, float]:
    return {
        "step": float(step),
        "time": time_value,
        "energy": compute_energy(u, v, dx, dy),
        "enstrophy": compute_enstrophy(vorticity, dx, dy),
        "max_velocity": compute_max_velocity(u, v),
        "cfl": cfl_number,
    }
