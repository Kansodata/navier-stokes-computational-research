import numpy as np
import pytest

from navier_stokes_research.metrics import (
    build_physical_diagnostics_payload,
    ensure_required_physical_diagnostics,
    total_enstrophy,
    total_kinetic_energy,
)


def test_kinetic_energy_zero_field_is_zero() -> None:
    u = np.zeros((4, 4), dtype=float)
    v = np.zeros((4, 4), dtype=float)
    assert total_kinetic_energy(u, v, dx=0.5, dy=0.5) == 0.0


def test_enstrophy_zero_field_is_zero() -> None:
    omega = np.zeros((4, 4), dtype=float)
    assert total_enstrophy(omega, dx=0.5, dy=0.5) == 0.0


def test_kinetic_energy_constant_field_matches_half_area() -> None:
    nx, ny = 4, 2
    dx, dy = 0.5, 1.0
    u = np.ones((nx, ny), dtype=float)
    v = np.zeros((nx, ny), dtype=float)
    area = nx * ny * dx * dy
    assert np.isclose(total_kinetic_energy(u, v, dx=dx, dy=dy), 0.5 * area)


def test_enstrophy_constant_field_matches_half_area() -> None:
    nx, ny = 3, 5
    dx, dy = 0.25, 0.4
    omega = np.ones((nx, ny), dtype=float)
    area = nx * ny * dx * dy
    assert np.isclose(total_enstrophy(omega, dx=dx, dy=dy), 0.5 * area)


def test_nan_or_inf_fields_raise_explicit_error() -> None:
    u = np.ones((2, 2), dtype=float)
    v_nan = np.array([[1.0, np.nan], [0.0, 1.0]], dtype=float)
    omega_inf = np.array([[1.0, np.inf], [0.0, 1.0]], dtype=float)
    with pytest.raises(ValueError, match="NaN or Inf"):
        total_kinetic_energy(u, v_nan, dx=1.0, dy=1.0)
    with pytest.raises(ValueError, match="NaN or Inf"):
        total_enstrophy(omega_inf, dx=1.0, dy=1.0)


def test_incompatible_shapes_raise_explicit_error() -> None:
    u = np.ones((2, 3), dtype=float)
    v = np.ones((3, 2), dtype=float)
    with pytest.raises(ValueError, match="identical shape"):
        total_kinetic_energy(u, v, dx=1.0, dy=1.0)


def test_diagnostics_payload_includes_required_keys() -> None:
    payload = build_physical_diagnostics_payload(
        energy=1.5,
        enstrophy=0.75,
        viscosity=1e-3,
        nx=64,
        ny=64,
        dt=0.0025,
        t=1.0,
        initial_condition="random",
        dealiasing_method="two_thirds",
    )
    ensure_required_physical_diagnostics(payload)
    assert payload["resolution"] == {"nx": 64, "ny": 64}
