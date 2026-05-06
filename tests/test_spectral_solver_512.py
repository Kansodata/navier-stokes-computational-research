from __future__ import annotations

import numpy as np
import pyfftw

from navier_stokes_research.solver import SpectralSolver512


def _smooth_vorticity() -> np.ndarray:
    x = np.linspace(0.0, 2.0 * np.pi, 512, endpoint=False)
    y = np.linspace(0.0, 2.0 * np.pi, 512, endpoint=False)
    xx, yy = np.meshgrid(x, y, indexing="ij")
    return np.sin(xx) * np.sin(yy)


def test_spectral_solver_512_uses_aligned_fftw_buffers_and_zero_mean_poisson() -> None:
    solver = SpectralSolver512(
        viscosity=1.0e-3,
        dt=1.0e-5,
        threads=1,
        fftw_effort="FFTW_ESTIMATE",
        spectrum_interval=1,
    )
    assert pyfftw.is_byte_aligned(solver.omega)
    assert pyfftw.is_byte_aligned(solver.omega_hat)

    solver.set_vorticity(_smooth_vorticity())
    solver.velocity()

    assert solver.psi_hat[0, 0] == 0.0
    assert abs(float(np.mean(solver.omega))) < 1.0e-14
    assert solver.audit_log[-1].spectrum is not None


def test_spectral_solver_512_rk4_step_is_finite_and_cfl_fail_closed() -> None:
    stable = SpectralSolver512(
        viscosity=1.0e-3,
        dt=1.0e-5,
        threads=1,
        fftw_effort="FFTW_ESTIMATE",
        spectrum_interval=1,
    )
    stable.set_vorticity(_smooth_vorticity())
    sample = stable.step()
    assert sample is not None
    assert sample.step == 1
    assert np.all(np.isfinite(stable.omega))
    assert stable.diagnostic_state()["scientific_acceptance"] == "human_review_required"

    unstable = SpectralSolver512(
        viscosity=1.0e-3,
        dt=1.0,
        threads=1,
        fftw_effort="FFTW_ESTIMATE",
    )
    unstable.set_vorticity(_smooth_vorticity())
    try:
        unstable.step()
    except FloatingPointError as exc:
        assert "CFL violation" in str(exc)
    else:
        raise AssertionError("Expected fail-closed CFL violation.")
