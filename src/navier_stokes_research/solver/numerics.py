from __future__ import annotations

import numpy as np


def build_wavenumbers(n: int, length: float) -> np.ndarray:
    return 2.0 * np.pi * np.fft.fftfreq(n, d=length / n)


def spectral_laplacian(kx: np.ndarray, ky: np.ndarray) -> np.ndarray:
    return -(kx[:, None] ** 2 + ky[None, :] ** 2)


def assert_finite(name: str, field: np.ndarray) -> None:
    if not np.all(np.isfinite(field)):
        raise FloatingPointError(f"{name} contains NaN or Inf values.")


def spectral_gradient(field_hat: np.ndarray, kx: np.ndarray, ky: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    ddx = np.fft.ifft2(1j * kx[:, None] * field_hat).real
    ddy = np.fft.ifft2(1j * ky[None, :] * field_hat).real
    return ddx, ddy


def dealias_mask(nx: int, ny: int) -> np.ndarray:
    cutoff_x = nx // 3
    cutoff_y = ny // 3
    freq_x = np.fft.fftfreq(nx) * nx
    freq_y = np.fft.fftfreq(ny) * ny
    mask_x = np.abs(freq_x) < cutoff_x
    mask_y = np.abs(freq_y) < cutoff_y
    return mask_x[:, None] & mask_y[None, :]


def apply_dealias(field_hat: np.ndarray, mask: np.ndarray) -> np.ndarray:
    if field_hat.shape != mask.shape:
        raise ValueError("field_hat and mask must have identical shape for de-aliasing.")
    return field_hat * mask
