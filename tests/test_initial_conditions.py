import numpy as np

from navier_stokes_research.config import GridConfig
from navier_stokes_research.initial_conditions.factory import gaussian_vortices, random_vorticity


def test_random_vorticity_is_deterministic() -> None:
    grid = GridConfig(nx=16, ny=16)
    first = random_vorticity(grid, amplitude=1.0, smoothing_sigma=4.0, seed=123)
    second = random_vorticity(grid, amplitude=1.0, smoothing_sigma=4.0, seed=123)
    assert np.allclose(first, second)


def test_gaussian_vortices_zero_mean() -> None:
    grid = GridConfig(nx=32, ny=32)
    field = gaussian_vortices(
        grid,
        amplitude=1.0,
        radius=0.25,
        strength=5.0,
        distance=1.0,
    )
    assert np.isclose(np.mean(field), 0.0, atol=1e-12)
