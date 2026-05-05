from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from navier_stokes_research.config import GridConfig, PhysicsConfig, TimeConfig
from navier_stokes_research.solver.numerics import (
    apply_dealias,
    assert_finite,
    build_wavenumbers,
    dealias_mask,
    spectral_gradient,
    spectral_laplacian,
)


@dataclass(frozen=True)
class StabilityState:
    cfl_number: float
    diffusion_number: float
    max_speed: float


class NavierStokesSpectralSolver:
    """Pseudo-spectral vorticity-streamfunction solver on a periodic domain."""

    def __init__(
        self,
        grid: GridConfig,
        physics: PhysicsConfig,
        time: TimeConfig,
    ) -> None:
        self.grid = grid
        self.physics = physics
        self.time = time

        self.dx = grid.lx / grid.nx
        self.dy = grid.ly / grid.ny
        self.kx = build_wavenumbers(grid.nx, grid.lx)
        self.ky = build_wavenumbers(grid.ny, grid.ly)
        self.laplacian = spectral_laplacian(self.kx, self.ky)
        self.inv_laplacian = np.zeros_like(self.laplacian, dtype=float)
        mask = self.laplacian != 0.0
        self.inv_laplacian[mask] = 1.0 / self.laplacian[mask]
        self.dealias = dealias_mask(grid.nx, grid.ny)

    def solve_streamfunction(self, vorticity: np.ndarray) -> np.ndarray:
        vorticity_hat = np.fft.fft2(vorticity)
        psi_hat = -self.inv_laplacian * vorticity_hat
        psi_hat[0, 0] = 0.0
        streamfunction = np.fft.ifft2(psi_hat).real
        assert_finite("streamfunction", streamfunction)
        return streamfunction

    def _velocity_from_vorticity_hat(self, vorticity_hat: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        psi_hat = -self.inv_laplacian * vorticity_hat
        psi_hat[0, 0] = 0.0
        u = np.fft.ifft2(1j * self.ky[None, :] * psi_hat).real
        v = np.fft.ifft2(-1j * self.kx[:, None] * psi_hat).real
        assert_finite("velocity_u", u)
        assert_finite("velocity_v", v)
        return u, v

    def velocity_from_vorticity(self, vorticity: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        return self._velocity_from_vorticity_hat(np.fft.fft2(vorticity))

    def compute_stability(self, vorticity: np.ndarray) -> StabilityState:
        u, v = self.velocity_from_vorticity(vorticity)
        max_speed = float(np.max(np.sqrt(u**2 + v**2)))
        cfl_number = self.time.dt * max_speed / min(self.dx, self.dy)
        diffusion_number = (
            self.physics.viscosity
            * self.time.dt
            * (2.0 / self.dx**2 + 2.0 / self.dy**2)
        )
        return StabilityState(
            cfl_number=cfl_number,
            diffusion_number=diffusion_number,
            max_speed=max_speed,
        )

    def ensure_stability(self, vorticity: np.ndarray) -> StabilityState:
        state = self.compute_stability(vorticity)
        if state.cfl_number > self.time.cfl_safety:
            raise ValueError(
                f"CFL violation: {state.cfl_number:.4f} > {self.time.cfl_safety:.4f}"
            )
        if state.diffusion_number > self.time.diffusion_safety:
            raise ValueError(
                "Diffusion stability violation: "
                f"{state.diffusion_number:.4f} > {self.time.diffusion_safety:.4f}"
            )
        return state

    def _rhs(self, vorticity: np.ndarray) -> np.ndarray:
        omega_hat = apply_dealias(np.fft.fft2(vorticity), self.dealias)
        u, v = self._velocity_from_vorticity_hat(omega_hat)
        dwdx, dwdy = spectral_gradient(omega_hat, self.kx, self.ky)
        laplace_omega = np.fft.ifft2(self.laplacian * omega_hat).real
        nonlinear = u * dwdx + v * dwdy
        nonlinear_hat = apply_dealias(np.fft.fft2(nonlinear), self.dealias)
        nonlinear_dealiased = np.fft.ifft2(nonlinear_hat).real
        rhs = -nonlinear_dealiased + self.physics.viscosity * laplace_omega
        assert_finite("nonlinear_dealiased", nonlinear_dealiased)
        assert_finite("rhs", rhs)
        return rhs

    def step(self, vorticity: np.ndarray) -> tuple[np.ndarray, StabilityState]:
        self.ensure_stability(vorticity)
        k1 = self._rhs(vorticity)
        predictor = vorticity + self.time.dt * k1
        assert_finite("predictor", predictor)
        k2 = self._rhs(predictor)
        updated = vorticity + 0.5 * self.time.dt * (k1 + k2)
        assert_finite("vorticity", updated)
        state = self.ensure_stability(updated)
        return updated, state
