from __future__ import annotations

import numpy as np

from navier_stokes_research.config import GridConfig, InitialConditionConfig


def _smooth_spectrum(field: np.ndarray, sigma: float) -> np.ndarray:
    nx, ny = field.shape
    kx = np.fft.fftfreq(nx) * nx
    ky = np.fft.fftfreq(ny) * ny
    kernel = np.exp(-(kx[:, None] ** 2 + ky[None, :] ** 2) / max(sigma**2, 1e-12))
    return np.fft.ifft2(np.fft.fft2(field) * kernel).real


def random_vorticity(
    grid: GridConfig,
    amplitude: float,
    smoothing_sigma: float,
    seed: int,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    raw = rng.standard_normal((grid.nx, grid.ny))
    smoothed = _smooth_spectrum(raw, smoothing_sigma)
    smoothed -= np.mean(smoothed)
    max_abs = np.max(np.abs(smoothed))
    return amplitude * smoothed / max(max_abs, 1e-12)


def gaussian_vortices(
    grid: GridConfig,
    amplitude: float,
    radius: float,
    strength: float,
    distance: float,
) -> np.ndarray:
    x = np.linspace(0.0, grid.lx, grid.nx, endpoint=False)
    y = np.linspace(0.0, grid.ly, grid.ny, endpoint=False)
    xx, yy = np.meshgrid(x, y, indexing="ij")
    cx = grid.lx / 2.0
    cy = grid.ly / 2.0

    def vortex(x0: float, y0: float, sign: float) -> np.ndarray:
        r2 = (xx - x0) ** 2 + (yy - y0) ** 2
        return sign * strength * np.exp(-r2 / (2.0 * radius**2))

    field = vortex(cx - distance / 2.0, cy, 1.0) + vortex(cx + distance / 2.0, cy, -1.0)
    field -= np.mean(field)
    max_abs = np.max(np.abs(field))
    return amplitude * field / max(max_abs, 1e-12)


def create_initial_vorticity(
    config: InitialConditionConfig,
    grid: GridConfig,
) -> np.ndarray:
    if config.kind == "random":
        return random_vorticity(
            grid=grid,
            amplitude=config.amplitude,
            smoothing_sigma=config.smoothing_sigma,
            seed=config.seed,
        )
    if config.kind == "vortices":
        return gaussian_vortices(
            grid=grid,
            amplitude=config.amplitude,
            radius=config.vortex_radius,
            strength=config.vortex_strength,
            distance=config.vortex_distance,
        )
    if config.kind == "taylor_green_2d":
        x = np.linspace(0.0, grid.lx, grid.nx, endpoint=False)
        y = np.linspace(0.0, grid.ly, grid.ny, endpoint=False)
        xx, yy = np.meshgrid(x, y, indexing="ij")
        return 2.0 * config.amplitude * np.sin(xx) * np.sin(yy)
    raise ValueError(f"Unsupported initial condition kind: {config.kind}")
