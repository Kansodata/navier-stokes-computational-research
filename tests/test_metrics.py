import numpy as np

from navier_stokes_research.metrics import compute_energy, compute_enstrophy, compute_max_velocity


def test_metrics_return_expected_scalars() -> None:
    u = np.array([[1.0, 0.0], [0.0, 1.0]])
    v = np.array([[1.0, 1.0], [0.0, 0.0]])
    w = np.array([[2.0, 0.0], [0.0, -2.0]])
    assert np.isclose(compute_energy(u, v, 1.0, 1.0), 2.0)
    assert np.isclose(compute_enstrophy(w, 1.0, 1.0), 4.0)
    assert np.isclose(compute_max_velocity(u, v), np.sqrt(2.0))
