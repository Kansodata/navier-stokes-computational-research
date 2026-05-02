import numpy as np
import pytest

from navier_stokes_research.config import GridConfig, PhysicsConfig, TimeConfig
from navier_stokes_research.solver import NavierStokesSpectralSolver


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
