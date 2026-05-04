from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from navier_stokes_research.metrics.physical import total_kinetic_energy
from navier_stokes_research.spectral_diagnostics import (
    compute_high_wavenumber_energy_fraction,
    compute_velocity_energy_spectrum_2d,
    write_spectral_diagnostics_json,
)


def test_zero_field_spectrum_is_zero() -> None:
    u = np.zeros((8, 8), dtype=float)
    v = np.zeros((8, 8), dtype=float)
    diagnostics = compute_velocity_energy_spectrum_2d(u, v, lx=2.0 * np.pi, ly=2.0 * np.pi)
    assert diagnostics["total_spectral_energy"] == 0.0
    assert all(value >= 0.0 for value in diagnostics["radial_energy"])
    assert diagnostics["high_wavenumber_energy_fraction"] == 0.0


def test_constant_field_energy_matches_physical_energy() -> None:
    nx, ny = 16, 16
    lx, ly = 2.0 * np.pi, 2.0 * np.pi
    u = np.ones((nx, ny), dtype=float)
    v = np.zeros((nx, ny), dtype=float)
    diagnostics = compute_velocity_energy_spectrum_2d(u, v, lx=lx, ly=ly)
    dx = lx / nx
    dy = ly / ny
    physical_energy = total_kinetic_energy(u, v, dx=dx, dy=dy)
    assert np.isclose(diagnostics["total_spectral_energy"], physical_energy, rtol=1e-10, atol=1e-12)
    radial_energy = np.asarray(diagnostics["radial_energy"], dtype=float)
    assert radial_energy[0] > 0.0
    assert np.allclose(radial_energy[1:], 0.0, atol=1e-12)
    assert diagnostics["high_wavenumber_energy_fraction"] == 0.0


def test_sinusoidal_field_energy_matches_physical_energy() -> None:
    nx, ny = 32, 32
    lx, ly = 2.0 * np.pi, 2.0 * np.pi
    x = np.linspace(0.0, lx, nx, endpoint=False)
    y = np.linspace(0.0, ly, ny, endpoint=False)
    xx, yy = np.meshgrid(x, y, indexing="ij")
    u = np.sin(xx)
    v = 0.5 * np.cos(yy)
    diagnostics = compute_velocity_energy_spectrum_2d(u, v, lx=lx, ly=ly)
    dx = lx / nx
    dy = ly / ny
    physical_energy = total_kinetic_energy(u, v, dx=dx, dy=dy)
    assert diagnostics["total_spectral_energy"] > 0.0
    assert np.isclose(diagnostics["total_spectral_energy"], physical_energy, rtol=1e-10, atol=1e-12)
    assert all(value >= 0.0 for value in diagnostics["radial_energy"])


def test_fail_closed_input_validation() -> None:
    u = np.ones((4, 4), dtype=float)
    v = np.ones((4, 4), dtype=float)
    with pytest.raises(ValueError, match="NaN or Inf"):
        bad_u = u.copy()
        bad_u[0, 0] = np.nan
        compute_velocity_energy_spectrum_2d(bad_u, v, lx=1.0, ly=1.0)
    with pytest.raises(ValueError, match="NaN or Inf"):
        bad_v = v.copy()
        bad_v[0, 0] = np.inf
        compute_velocity_energy_spectrum_2d(u, bad_v, lx=1.0, ly=1.0)
    with pytest.raises(ValueError, match="identical shape"):
        compute_velocity_energy_spectrum_2d(np.ones((4, 3)), np.ones((3, 4)), lx=1.0, ly=1.0)
    with pytest.raises(ValueError, match="2D array"):
        compute_velocity_energy_spectrum_2d(np.ones(4), np.ones(4), lx=1.0, ly=1.0)
    with pytest.raises(ValueError, match="must be > 0"):
        compute_velocity_energy_spectrum_2d(u, v, lx=0.0, ly=1.0)


def test_high_wavenumber_fraction_input_validation() -> None:
    k = np.array([0.0, 1.0, 2.0])
    e = np.array([1.0, 0.5, 0.1])
    with pytest.raises(ValueError, match="0 < cutoff_fraction < 1"):
        compute_high_wavenumber_energy_fraction(k, e, cutoff_fraction=1.0)
    with pytest.raises(ValueError, match="non-negative"):
        compute_high_wavenumber_energy_fraction(k, np.array([1.0, -1.0, 0.2]))


def test_write_spectral_diagnostics_json_creates_file(tmp_path: Path) -> None:
    diagnostics = compute_velocity_energy_spectrum_2d(
        np.zeros((8, 8), dtype=float),
        np.zeros((8, 8), dtype=float),
        lx=2.0 * np.pi,
        ly=2.0 * np.pi,
    )
    target = tmp_path / "diag" / "spectral.json"
    written = write_spectral_diagnostics_json(target, diagnostics)
    assert written.exists()
    payload = json.loads(written.read_text(encoding="utf-8"))
    for key in (
        "total_spectral_energy",
        "radial_wavenumbers",
        "radial_energy",
        "high_wavenumber_energy_fraction",
        "max_resolved_wavenumber",
        "nyquist_wavenumber_estimate",
        "grid",
        "domain",
        "normalization",
    ):
        assert key in payload
