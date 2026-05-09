from __future__ import annotations

"""Baseline 2D periodic pseudo-spectral Navier-Stokes solver.

The solver uses the vorticity-streamfunction formulation on a periodic Fourier
grid. It exposes stability checks, velocity recovery, streamfunction recovery,
and a second-order predictor-corrector time step. The implementation remains
limited to the 2D computational model validated elsewhere in the repository.
"""

from dataclasses import dataclass

import numpy as np

from navier_stokes_research.config import ForcingConfig, GridConfig, PhysicsConfig, TimeConfig
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
    """Computed CFL, diffusion, and speed diagnostics for one solver state."""

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
        forcing: ForcingConfig | None = None,
    ) -> None:
        self.grid = grid
        self.physics = physics
        self.time = time
        self.forcing = forcing or ForcingConfig()

        self.dx = grid.lx / grid.nx
        self.dy = grid.ly / grid.ny
        self.kx = build_wavenumbers(grid.nx, grid.lx)
        self.ky = build_wavenumbers(grid.ny, grid.ly)
        self.laplacian = spectral_laplacian(self.kx, self.ky)
        self.inv_laplacian = np.zeros_like(self.laplacian, dtype=float)
        mask = self.laplacian != 0.0
        self.inv_laplacian[mask] = 1.0 / self.laplacian[mask]
        self.dealias = dealias_mask(grid.nx, grid.ny)
        self.forcing_mask = self._build_forcing_mask()
        self._forcing_rng = np.random.default_rng(self.forcing.seed)
        self.forcing_field = self._build_initial_forcing_field()

    def _build_forcing_mask(self) -> np.ndarray:
        wavenumber_radius = np.sqrt(self.kx[:, None] ** 2 + self.ky[None, :] ** 2)
        mask = (
            (wavenumber_radius >= self.forcing.k_min)
            & (wavenumber_radius <= self.forcing.k_max)
            & (wavenumber_radius > 0.0)
        )
        return mask & self.dealias

    def _scaled_band_limited_random_field(self) -> np.ndarray:
        active_modes = int(np.count_nonzero(self.forcing_mask))
        if active_modes == 0:
            raise ValueError("Fourier forcing band contains no active de-aliased modes")

        raw = self._forcing_rng.normal(size=(self.grid.nx, self.grid.ny))
        forcing_hat = np.fft.fft2(raw)
        forcing_hat = apply_dealias(forcing_hat * self.forcing_mask, self.dealias)
        forcing_hat[0, 0] = 0.0
        forcing = np.fft.ifft2(forcing_hat).real
        forcing -= float(np.mean(forcing))
        rms = float(np.sqrt(np.mean(forcing**2)))
        if not np.isfinite(rms) or rms <= 0.0:
            raise ValueError("Fourier forcing generated zero or non-finite RMS")
        forcing *= self.forcing.target_energy_input_rate / rms
        assert_finite("fourier_forcing_sample", forcing)
        return forcing

    def _build_initial_forcing_field(self) -> np.ndarray:
        if not self.forcing.enabled:
            return np.zeros((self.grid.nx, self.grid.ny), dtype=float)
        if self.forcing.forcing_type not in {
            "fourier_deterministic_narrow_band",
            "fourier_ou_narrow_band",
        }:
            raise ValueError(f"Unsupported runtime forcing_type: {self.forcing.forcing_type}")
        return self._scaled_band_limited_random_field()

    def _advance_forcing_state(self) -> None:
        if not self.forcing.enabled or self.forcing.forcing_type != "fourier_ou_narrow_band":
            return
        decay = float(np.exp(-self.time.dt / self.forcing.ou_correlation_time))
        innovation_scale = self.forcing.ou_noise_amplitude * float(np.sqrt(max(0.0, 1.0 - decay**2)))
        innovation = self._scaled_band_limited_random_field()
        next_forcing = decay * self.forcing_field + innovation_scale * innovation
        next_forcing -= float(np.mean(next_forcing))
        rms = float(np.sqrt(np.mean(next_forcing**2)))
        if not np.isfinite(rms) or rms <= 0.0:
            raise ValueError("OU Fourier forcing generated zero or non-finite RMS")
        next_forcing *= self.forcing.target_energy_input_rate / rms
        assert_finite("ou_forcing_state", next_forcing)
        self.forcing_field = next_forcing

    def solve_streamfunction(self, vorticity: np.ndarray) -> np.ndarray:
        """Recover the zero-mean streamfunction from a real vorticity field."""

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
        """Recover the incompressible velocity components from vorticity."""

        return self._velocity_from_vorticity_hat(np.fft.fft2(vorticity))

    def compute_stability(self, vorticity: np.ndarray) -> StabilityState:
        """Compute CFL and diffusion diagnostics without mutating solver state."""

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
        """Return stability diagnostics or fail closed on configured limits."""

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
        omega_dealiased = np.fft.ifft2(omega_hat).real
        u, v = self._velocity_from_vorticity_hat(omega_hat)
        dwdx, dwdy = spectral_gradient(omega_hat, self.kx, self.ky)
        laplace_omega = np.fft.ifft2(self.laplacian * omega_hat).real
        nonlinear = u * dwdx + v * dwdy
        nonlinear_hat = apply_dealias(np.fft.fft2(nonlinear), self.dealias)
        nonlinear_dealiased = np.fft.ifft2(nonlinear_hat).real
        ekman_drag = -self.forcing.ekman_drag * omega_dealiased
        rhs = (
            -nonlinear_dealiased
            + self.physics.viscosity * laplace_omega
            + ekman_drag
            + self.forcing_field
        )
        assert_finite("omega_dealiased", omega_dealiased)
        assert_finite("nonlinear_dealiased", nonlinear_dealiased)
        assert_finite("ekman_drag", ekman_drag)
        assert_finite("forcing_field", self.forcing_field)
        assert_finite("rhs", rhs)
        return rhs

    def step(self, vorticity: np.ndarray) -> tuple[np.ndarray, StabilityState]:
        """Advance vorticity by one predictor-corrector time step.

        The method validates stability before and after the update and advances
        the forcing state after a finite, stable vorticity field is produced.
        """

        self.ensure_stability(vorticity)
        k1 = self._rhs(vorticity)
        predictor = vorticity + self.time.dt * k1
        assert_finite("predictor", predictor)
        k2 = self._rhs(predictor)
        updated = vorticity + 0.5 * self.time.dt * (k1 + k2)
        assert_finite("vorticity", updated)
        state = self.ensure_stability(updated)
        self._advance_forcing_state()
        return updated, state
