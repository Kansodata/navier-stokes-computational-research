from __future__ import annotations

"""Numerical helper routines for the 2D periodic pseudo-spectral solver.

This module contains small Fourier-space utilities used by the solver layer:
wavenumber construction, spectral derivatives, Laplacian construction,
finite-value checks, and 2/3-rule de-aliasing. The functions are intentionally
stateless and do not encode physical claims beyond the periodic Fourier grid
assumptions visible in their inputs.
"""

import numpy as np


def build_wavenumbers(n: int, length: float) -> np.ndarray:
    """Return angular Fourier wavenumbers for a periodic domain.

    Parameters:
        n: Number of grid points along one periodic axis.
        length: Physical domain length along that axis.

    Returns:
        One-dimensional array of angular wavenumbers compatible with NumPy FFT
        ordering.
    """

    return 2.0 * np.pi * np.fft.fftfreq(n, d=length / n)


def spectral_laplacian(kx: np.ndarray, ky: np.ndarray) -> np.ndarray:
    """Build the Fourier symbol for the 2D Laplacian operator."""

    return -(kx[:, None] ** 2 + ky[None, :] ** 2)


def assert_finite(name: str, field: np.ndarray) -> None:
    """Fail closed when a numerical field contains NaN or Inf values."""

    if not np.all(np.isfinite(field)):
        raise FloatingPointError(f"{name} contains NaN or Inf values.")


def spectral_gradient(field_hat: np.ndarray, kx: np.ndarray, ky: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return real-space gradients from a 2D Fourier-space scalar field.

    The derivative convention follows the periodic Fourier representation used
    by NumPy FFTs: differentiation in spectral space is multiplication by
    ``1j * k`` followed by an inverse transform.
    """

    ddx = np.fft.ifft2(1j * kx[:, None] * field_hat).real
    ddy = np.fft.ifft2(1j * ky[None, :] * field_hat).real
    return ddx, ddy


def dealias_mask(nx: int, ny: int) -> np.ndarray:
    """Return the 2/3-rule Orszag de-aliasing mask for a 2D Fourier grid."""

    cutoff_x = nx // 3
    cutoff_y = ny // 3
    freq_x = np.fft.fftfreq(nx) * nx
    freq_y = np.fft.fftfreq(ny) * ny
    mask_x = np.abs(freq_x) < cutoff_x
    mask_y = np.abs(freq_y) < cutoff_y
    return mask_x[:, None] & mask_y[None, :]


def apply_dealias(field_hat: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Apply a spectral de-aliasing mask with shape validation."""

    if field_hat.shape != mask.shape:
        raise ValueError("field_hat and mask must have identical shape for de-aliasing.")
    return field_hat * mask
