import numpy as np
import pytest

from navier_stokes_research.config import GridConfig, PhysicsConfig, TimeConfig
from navier_stokes_research.solver import NavierStokesSpectralSolver
from navier_stokes_research.solver.numerics import dealias_mask


def test_zero_vorticity_stays_zero() -> None:
    solver = NavierStokesSpectralSolver(
        grid=GridConfig(nx=16, ny=16),
        physics=PhysicsConfig(viscosity=0.01),
        time=TimeConfig(dt=0.01, steps=10),
    )
    vorticity = np.zeros((16, 16))
    updated, state = solver.step(vorticity)
    assert np.allclose(updated, 0.0)
    assert state.cfl_number == 0.0


def test_cfl_violation_raises() -> None:
    solver = NavierStokesSpectralSolver(
        grid=GridConfig(nx=16, ny=16),
        physics=PhysicsConfig(viscosity=0.0),
        time=TimeConfig(dt=0.5, steps=10, cfl_safety=0.1),
    )
    x = np.linspace(0.0, 2.0 * np.pi, 16, endpoint=False)
    xx, yy = np.meshgrid(x, x, indexing="ij")
    vorticity = np.sin(xx) + np.cos(yy)
    with pytest.raises(ValueError, match="CFL violation"):
        solver.ensure_stability(vorticity)


def test_orszag_two_thirds_mask_eliminates_high_modes() -> None:
    mask = dealias_mask(12, 12)
    assert mask.shape == (12, 12)
    assert bool(mask[0, 0])
    # Mode index 4 maps to frequency +/-4 for N=12, above cutoff (N/3 = 4, strict <).
    assert not bool(mask[4, 0])
    assert not bool(mask[0, 4])
    assert not bool(mask[4, 4])


def test_dealiasing_can_be_disabled_for_controlled_comparison() -> None:
    solver = NavierStokesSpectralSolver(
        grid=GridConfig(nx=12, ny=12),
        physics=PhysicsConfig(viscosity=0.001, dealiasing_enabled=False),
        time=TimeConfig(dt=0.002, steps=1),
    )
    assert np.all(solver.dealias)


def test_solver_fails_closed_on_non_finite_state() -> None:
    solver = NavierStokesSpectralSolver(
        grid=GridConfig(nx=16, ny=16),
        physics=PhysicsConfig(viscosity=0.01),
        time=TimeConfig(dt=0.01, steps=10),
    )
    vorticity = np.zeros((16, 16))
    vorticity[0, 0] = np.nan
    with pytest.raises(FloatingPointError, match="NaN or Inf"):
        solver.step(vorticity)
