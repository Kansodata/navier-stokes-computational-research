from __future__ import annotations

import numpy as np
import pytest

from navier_stokes_research.config import GridConfig, PhysicsConfig, TimeConfig
from navier_stokes_research.solver import NavierStokesSpectralSolver
from navier_stokes_research.solver.numerics import apply_dealias, spectral_gradient


def test_zero_vorticity_stays_zero() -> None:
    solver = NavierStokesSpectralSolver(
        grid=GridConfig(nx=16, ny=16),
        physics=PhysicsConfig(viscosity=0.001),
        time=TimeConfig(dt=0.001, steps=1),
    )
    vorticity = np.zeros((16, 16))
    updated, state = solver.step(vorticity)
    assert np.allclose(updated, 0.0)
    assert state.max_speed == pytest.approx(0.0)


def test_cfl_violation_raises() -> None:
    solver = NavierStokesSpectralSolver(
        grid=GridConfig(nx=16, ny=16),
        physics=PhysicsConfig(viscosity=0.001),
        time=TimeConfig(dt=10.0, steps=1, cfl_safety=0.01),
    )
    x = np.linspace(0.0, 2.0 * np.pi, 16, endpoint=False)
    y = np.linspace(0.0, 2.0 * np.pi, 16, endpoint=False)
    xx, yy = np.meshgrid(x, y, indexing="ij")
    vorticity = np.sin(xx) + np.cos(yy)
    with pytest.raises(ValueError, match="CFL violation"):
        solver.ensure_stability(vorticity)


def test_apply_dealias_requires_matching_shape() -> None:
    field_hat = np.zeros((8, 8), dtype=complex)
    mask = np.ones((8, 4), dtype=bool)
    with pytest.raises(ValueError, match="identical shape"):
        apply_dealias(field_hat, mask)


def test_rhs_is_finite_for_deterministic_field() -> None:
    solver = NavierStokesSpectralSolver(
        grid=GridConfig(nx=32, ny=32),
        physics=PhysicsConfig(viscosity=0.001),
        time=TimeConfig(dt=0.0015, steps=8),
    )
    x = np.linspace(0.0, 2.0 * np.pi, 32, endpoint=False)
    xx, yy = np.meshgrid(x, x, indexing="ij")
    vorticity = np.sin(xx) + 0.5 * np.cos(2.0 * yy)
    rhs = solver._rhs(vorticity)
    assert np.all(np.isfinite(rhs))


def test_rhs_applies_dealias_to_velocity_and_full_nonlinear_term() -> None:
    solver = NavierStokesSpectralSolver(
        grid=GridConfig(nx=32, ny=32),
        physics=PhysicsConfig(viscosity=0.001),
        time=TimeConfig(dt=0.0015, steps=4),
    )
    x = np.linspace(0.0, 2.0 * np.pi, 32, endpoint=False)
    xx, yy = np.meshgrid(x, x, indexing="ij")
    vorticity = (
        np.sin(7.0 * xx) * np.cos(5.0 * yy)
        + 0.5 * np.cos(9.0 * xx - 3.0 * yy)
        + 0.25 * np.sin(11.0 * xx + 7.0 * yy)
    )

    omega_hat = apply_dealias(np.fft.fft2(vorticity), solver.dealias)
    u, v = solver._velocity_from_vorticity_hat(omega_hat)
    dwdx, dwdy = spectral_gradient(omega_hat, solver.kx, solver.ky)
    laplace_omega = np.fft.ifft2(solver.laplacian * omega_hat).real

    nonlinear = u * dwdx + v * dwdy
    nonlinear_hat_dealiased = apply_dealias(np.fft.fft2(nonlinear), solver.dealias)
    nonlinear_dealiased = np.fft.ifft2(nonlinear_hat_dealiased).real
    rhs_expected = -nonlinear_dealiased + solver.physics.viscosity * laplace_omega

    u_unfiltered, v_unfiltered = solver.velocity_from_vorticity(vorticity)
    nonlinear_unfiltered_velocity = u_unfiltered * dwdx + v_unfiltered * dwdy
    rhs_unfiltered_velocity = (
        -np.fft.ifft2(apply_dealias(np.fft.fft2(nonlinear_unfiltered_velocity), solver.dealias)).real
        + solver.physics.viscosity * laplace_omega
    )

    rhs_solver = solver._rhs(vorticity)
    assert np.allclose(rhs_solver, rhs_expected, atol=1e-12, rtol=1e-12)
    assert not np.allclose(rhs_solver, rhs_unfiltered_velocity, atol=1e-14, rtol=1e-14)
