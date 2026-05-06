from __future__ import annotations

import numpy as np
import pytest

from navier_stokes_research.config import ForcingConfig, GridConfig, PhysicsConfig, TimeConfig
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


def test_default_ekman_drag_is_no_op_for_rhs() -> None:
    grid = GridConfig(nx=32, ny=32)
    physics = PhysicsConfig(viscosity=0.001)
    time = TimeConfig(dt=0.0015, steps=4)
    solver_default = NavierStokesSpectralSolver(grid=grid, physics=physics, time=time)
    solver_explicit_noop = NavierStokesSpectralSolver(
        grid=grid,
        physics=physics,
        time=time,
        forcing=ForcingConfig(ekman_drag=0.0),
    )
    x = np.linspace(0.0, 2.0 * np.pi, 32, endpoint=False)
    xx, yy = np.meshgrid(x, x, indexing="ij")
    vorticity = np.sin(2.0 * xx) + 0.5 * np.cos(3.0 * yy)

    assert np.allclose(solver_default._rhs(vorticity), solver_explicit_noop._rhs(vorticity))


def test_ekman_drag_adds_negative_vorticity_proportional_rhs_term() -> None:
    grid = GridConfig(nx=32, ny=32)
    physics = PhysicsConfig(viscosity=0.0)
    time = TimeConfig(dt=0.001, steps=1)
    alpha = 0.125
    solver_without_drag = NavierStokesSpectralSolver(grid=grid, physics=physics, time=time)
    solver_with_drag = NavierStokesSpectralSolver(
        grid=grid,
        physics=physics,
        time=time,
        forcing=ForcingConfig(ekman_drag=alpha),
    )
    x = np.linspace(0.0, 2.0 * np.pi, 32, endpoint=False)
    xx, yy = np.meshgrid(x, x, indexing="ij")
    vorticity = np.sin(2.0 * xx) + 0.25 * np.cos(3.0 * yy)
    omega_hat = apply_dealias(np.fft.fft2(vorticity), solver_with_drag.dealias)
    omega_dealiased = np.fft.ifft2(omega_hat).real

    drag_contribution = solver_with_drag._rhs(vorticity) - solver_without_drag._rhs(vorticity)

    assert np.allclose(drag_contribution, -alpha * omega_dealiased, atol=1e-12, rtol=1e-12)


def test_deterministic_fourier_forcing_is_seed_reproducible_and_mean_zero() -> None:
    forcing = ForcingConfig(
        enabled=True,
        forcing_type="fourier_deterministic_narrow_band",
        k_min=2.0,
        k_max=4.0,
        seed=123,
        target_energy_input_rate=0.01,
    )
    solver_a = NavierStokesSpectralSolver(
        grid=GridConfig(nx=32, ny=32),
        physics=PhysicsConfig(viscosity=0.0),
        time=TimeConfig(dt=0.001, steps=1),
        forcing=forcing,
    )
    solver_b = NavierStokesSpectralSolver(
        grid=GridConfig(nx=32, ny=32),
        physics=PhysicsConfig(viscosity=0.0),
        time=TimeConfig(dt=0.001, steps=1),
        forcing=forcing,
    )

    assert np.allclose(solver_a.forcing_field, solver_b.forcing_field)
    assert float(np.mean(solver_a.forcing_field)) == pytest.approx(0.0, abs=1e-15)
    assert np.all(np.isfinite(solver_a.forcing_field))


def test_deterministic_fourier_forcing_is_band_limited_and_dealiased() -> None:
    forcing = ForcingConfig(
        enabled=True,
        forcing_type="fourier_deterministic_narrow_band",
        k_min=2.0,
        k_max=4.0,
        seed=123,
        target_energy_input_rate=0.01,
    )
    solver = NavierStokesSpectralSolver(
        grid=GridConfig(nx=32, ny=32),
        physics=PhysicsConfig(viscosity=0.0),
        time=TimeConfig(dt=0.001, steps=1),
        forcing=forcing,
    )
    forcing_hat = np.fft.fft2(solver.forcing_field)
    outside_active_band = ~solver.forcing_mask

    assert np.count_nonzero(solver.forcing_mask) > 0
    assert np.allclose(forcing_hat[outside_active_band], 0.0, atol=1e-10)


def test_deterministic_fourier_forcing_contributes_to_rhs_when_enabled() -> None:
    forcing = ForcingConfig(
        enabled=True,
        forcing_type="fourier_deterministic_narrow_band",
        k_min=2.0,
        k_max=4.0,
        seed=321,
        target_energy_input_rate=0.01,
    )
    grid = GridConfig(nx=32, ny=32)
    physics = PhysicsConfig(viscosity=0.0)
    time = TimeConfig(dt=0.001, steps=1)
    solver_without_forcing = NavierStokesSpectralSolver(grid=grid, physics=physics, time=time)
    solver_with_forcing = NavierStokesSpectralSolver(
        grid=grid,
        physics=physics,
        time=time,
        forcing=forcing,
    )
    vorticity = np.zeros((32, 32))

    rhs_delta = solver_with_forcing._rhs(vorticity) - solver_without_forcing._rhs(vorticity)

    assert np.allclose(rhs_delta, solver_with_forcing.forcing_field, atol=1e-12, rtol=1e-12)


def test_deterministic_fourier_forcing_fails_closed_for_empty_active_band() -> None:
    forcing = ForcingConfig(
        enabled=True,
        forcing_type="fourier_deterministic_narrow_band",
        k_min=10_000.0,
        k_max=10_001.0,
        seed=321,
        target_energy_input_rate=0.01,
    )

    with pytest.raises(ValueError, match="contains no active de-aliased modes"):
        NavierStokesSpectralSolver(
            grid=GridConfig(nx=32, ny=32),
            physics=PhysicsConfig(viscosity=0.0),
            time=TimeConfig(dt=0.001, steps=1),
            forcing=forcing,
        )
