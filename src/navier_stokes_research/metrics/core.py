from __future__ import annotations

import numpy as np

from .physical import total_enstrophy, total_kinetic_energy


def compute_energy(u: np.ndarray, v: np.ndarray, dx: float, dy: float) -> float:
    return total_kinetic_energy(u=u, v=v, dx=dx, dy=dy)


def compute_enstrophy(vorticity: np.ndarray, dx: float, dy: float) -> float:
    return total_enstrophy(vorticity=vorticity, dx=dx, dy=dy)


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
