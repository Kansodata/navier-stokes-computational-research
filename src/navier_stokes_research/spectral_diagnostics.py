from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from navier_stokes_research.solver.numerics import build_wavenumbers


def _as_2d_finite_array(name: str, values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim != 2:
        raise ValueError(f"{name} must be a 2D array.")
    if array.size == 0:
        raise ValueError(f"{name} must be non-empty.")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains NaN or Inf values.")
    return array


def _as_positive_float(name: str, value: float) -> float:
    number = float(value)
    if not np.isfinite(number):
        raise ValueError(f"{name} must be finite.")
    if number <= 0.0:
        raise ValueError(f"{name} must be > 0.")
    return number


def compute_high_wavenumber_energy_fraction(
    radial_wavenumbers: np.ndarray | list[float],
    radial_energy: np.ndarray | list[float],
    cutoff_fraction: float = 2.0 / 3.0,
) -> float:
    k = np.asarray(radial_wavenumbers, dtype=float)
    energy = np.asarray(radial_energy, dtype=float)
    if k.ndim != 1 or energy.ndim != 1:
        raise ValueError("radial_wavenumbers and radial_energy must be 1D arrays.")
    if k.shape != energy.shape:
        raise ValueError("radial_wavenumbers and radial_energy must have identical shape.")
    if k.size == 0:
        raise ValueError("radial arrays must be non-empty.")
    if not np.all(np.isfinite(k)) or not np.all(np.isfinite(energy)):
        raise ValueError("radial arrays contain NaN or Inf values.")
    if np.any(energy < 0.0):
        raise ValueError("radial_energy must be non-negative.")
    cutoff = float(cutoff_fraction)
    if not np.isfinite(cutoff) or not (0.0 < cutoff < 1.0):
        raise ValueError("cutoff_fraction must satisfy 0 < cutoff_fraction < 1.")

    total = float(np.sum(energy))
    if total <= 0.0:
        return 0.0
    k_max = float(np.max(k))
    if k_max <= 0.0:
        return 0.0
    threshold = cutoff * k_max
    high_energy = float(np.sum(energy[k >= threshold]))
    return high_energy / total


def compute_velocity_energy_spectrum_2d(u: np.ndarray, v: np.ndarray, lx: float, ly: float) -> dict:
    u_field = _as_2d_finite_array("u", u)
    v_field = _as_2d_finite_array("v", v)
    if u_field.shape != v_field.shape:
        raise ValueError("u and v must have identical shape.")
    lx_value = _as_positive_float("lx", lx)
    ly_value = _as_positive_float("ly", ly)

    nx, ny = u_field.shape
    dx = lx_value / nx
    dy = ly_value / ny
    sample_count = nx * ny

    u_hat = np.fft.fft2(u_field)
    v_hat = np.fft.fft2(v_field)
    modal_energy = 0.5 * (dx * dy / sample_count) * (np.abs(u_hat) ** 2 + np.abs(v_hat) ** 2)

    kx = build_wavenumbers(nx, lx_value)
    ky = build_wavenumbers(ny, ly_value)
    k_mag = np.sqrt(kx[:, None] ** 2 + ky[None, :] ** 2)

    dk = min(2.0 * np.pi / lx_value, 2.0 * np.pi / ly_value)
    shell_index = np.floor(k_mag / dk + 1e-12).astype(int)
    max_shell = int(shell_index.max())
    radial_energy = np.zeros(max_shell + 1, dtype=float)
    for shell in range(max_shell + 1):
        radial_energy[shell] = float(np.sum(modal_energy[shell_index == shell]))
    radial_wavenumbers = np.arange(max_shell + 1, dtype=float) * dk

    high_fraction = compute_high_wavenumber_energy_fraction(
        radial_wavenumbers=radial_wavenumbers,
        radial_energy=radial_energy,
        cutoff_fraction=2.0 / 3.0,
    )

    nyquist_x = np.pi / dx
    nyquist_y = np.pi / dy
    diagnostics = {
        "total_spectral_energy": float(np.sum(modal_energy)),
        "radial_wavenumbers": radial_wavenumbers.tolist(),
        "radial_energy": radial_energy.tolist(),
        "high_wavenumber_energy_fraction": float(high_fraction),
        "max_resolved_wavenumber": float(np.max(k_mag)),
        "nyquist_wavenumber_estimate": float(np.sqrt(nyquist_x**2 + nyquist_y**2)),
        "grid": {"nx": int(nx), "ny": int(ny)},
        "domain": {"lx": lx_value, "ly": ly_value},
        "normalization": {
            "fft_convention": "numpy_fft2",
            "parseval_scaling": "0.5 * (dx*dy/(nx*ny)) * (|u_hat|^2 + |v_hat|^2)",
            "radial_binning": "shell_index = floor(|k| / dk), dk=min(2pi/lx,2pi/ly)",
        },
    }
    return diagnostics


def write_spectral_diagnostics_json(path: str | Path, diagnostics: dict) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    return destination
