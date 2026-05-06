from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import numpy as np
import pyfftw


@dataclass(frozen=True)
class SpectralAuditSample:
    step: int
    time: float
    energy: float
    enstrophy: float
    max_velocity: float
    cfl_number: float
    spectrum: dict[str, list[float]] | None


class SpectralSolver512:
    """High-throughput 2D periodic vorticity-streamfunction solver for 512x512 runs.

    This class is intentionally separate from the baseline solver. It is an opt-in
    HPC implementation for controlled 2D experiments and does not expand the
    scientific scope beyond periodic incompressible 2D Navier-Stokes diagnostics.
    """

    def __init__(
        self,
        *,
        viscosity: float,
        dt: float,
        cfl_safety: float = 0.5,
        length: float = 2.0 * np.pi,
        nx: int = 512,
        ny: int = 512,
        threads: int | None = None,
        fftw_effort: str = "FFTW_MEASURE",
        enstrophy_growth_limit: float = 10.0,
        spectrum_interval: int = 50,
    ) -> None:
        if nx != 512 or ny != 512:
            raise ValueError("SpectralSolver512 is specialized for nx=ny=512.")
        if viscosity <= 0.0:
            raise ValueError("viscosity must be positive.")
        if dt <= 0.0:
            raise ValueError("dt must be positive.")
        if cfl_safety <= 0.0:
            raise ValueError("cfl_safety must be positive.")
        if enstrophy_growth_limit <= 1.0:
            raise ValueError("enstrophy_growth_limit must be greater than 1.")

        self.nx = nx
        self.ny = ny
        self.length = float(length)
        self.viscosity = float(viscosity)
        self.dt = float(dt)
        self.cfl_safety = float(cfl_safety)
        self.enstrophy_growth_limit = float(enstrophy_growth_limit)
        self.spectrum_interval = int(spectrum_interval)
        self.threads = int(threads or max(1, os.cpu_count() or 1))

        self.dx = self.length / self.nx
        self.dy = self.length / self.ny
        self.cell_area = self.dx * self.dy
        self.time = 0.0
        self.step_index = 0
        self.initial_enstrophy: float | None = None
        self.audit_log: list[SpectralAuditSample] = []

        freq_x = np.fft.fftfreq(self.nx, d=self.dx) * 2.0 * np.pi
        freq_y = np.fft.fftfreq(self.ny, d=self.dy) * 2.0 * np.pi
        self.kx = freq_x[:, None]
        self.ky = freq_y[None, :]
        self.k2 = self.kx**2 + self.ky**2
        self.inv_k2 = np.zeros_like(self.k2)
        nonzero = self.k2 > 0.0
        self.inv_k2[nonzero] = 1.0 / self.k2[nonzero]

        # CPU optimization: the 2/3 Orszag mask is built once and reused for every RHS.
        cutoff_x = self.nx // 3
        cutoff_y = self.ny // 3
        mode_x = np.fft.fftfreq(self.nx) * self.nx
        mode_y = np.fft.fftfreq(self.ny) * self.ny
        self.dealias = (np.abs(mode_x)[:, None] < cutoff_x) & (
            np.abs(mode_y)[None, :] < cutoff_y
        )

        # Memory optimization: all large work arrays are FFTW-aligned and persistent.
        self.omega = pyfftw.empty_aligned((self.nx, self.ny), dtype="float64")
        self.tmp = pyfftw.empty_aligned((self.nx, self.ny), dtype="float64")
        self.k1 = pyfftw.empty_aligned((self.nx, self.ny), dtype="float64")
        self.k2_stage = pyfftw.empty_aligned((self.nx, self.ny), dtype="float64")
        self.k3 = pyfftw.empty_aligned((self.nx, self.ny), dtype="float64")
        self.k4 = pyfftw.empty_aligned((self.nx, self.ny), dtype="float64")
        self.u = pyfftw.empty_aligned((self.nx, self.ny), dtype="float64")
        self.v = pyfftw.empty_aligned((self.nx, self.ny), dtype="float64")
        self.dwdx = pyfftw.empty_aligned((self.nx, self.ny), dtype="float64")
        self.dwdy = pyfftw.empty_aligned((self.nx, self.ny), dtype="float64")
        self.dpsidx = pyfftw.empty_aligned((self.nx, self.ny), dtype="float64")
        self.dpsidy = pyfftw.empty_aligned((self.nx, self.ny), dtype="float64")
        self.laplace = pyfftw.empty_aligned((self.nx, self.ny), dtype="float64")
        self.jacobian = pyfftw.empty_aligned((self.nx, self.ny), dtype="float64")

        self.omega_hat = pyfftw.empty_aligned((self.nx, self.ny), dtype="complex128")
        self.psi_hat = pyfftw.empty_aligned((self.nx, self.ny), dtype="complex128")
        self.work_hat = pyfftw.empty_aligned((self.nx, self.ny), dtype="complex128")
        self._fft_in = pyfftw.empty_aligned((self.nx, self.ny), dtype="complex128")
        self._ifft_in = pyfftw.empty_aligned((self.nx, self.ny), dtype="complex128")

        # CPU optimization: pyfftw.builders creates FFTW_MEASURE plans once; step() only executes them.
        self._forward_plan = pyfftw.builders.fft2(
            self._fft_in,
            axes=(0, 1),
            planner_effort=fftw_effort,
            threads=self.threads,
            avoid_copy=True,
        )
        self._backward_plan = pyfftw.builders.ifft2(
            self._ifft_in,
            axes=(0, 1),
            planner_effort=fftw_effort,
            threads=self.threads,
            avoid_copy=True,
        )

    def set_vorticity(self, vorticity: np.ndarray) -> None:
        if vorticity.shape != (self.nx, self.ny):
            raise ValueError("vorticity must have shape (512, 512).")
        np.copyto(self.omega, vorticity, casting="safe")
        self.omega -= float(np.mean(self.omega))
        self._assert_finite("initial_vorticity", self.omega)
        self.initial_enstrophy = self.enstrophy(self.omega)
        self._record_audit_sample(force_spectrum=True)

    def _fft2_real(self, field: np.ndarray, out_hat: np.ndarray) -> None:
        # Memory optimization: reuse the complex FFT input buffer instead of allocating.
        self._fft_in.real[:] = field
        self._fft_in.imag.fill(0.0)
        self._forward_plan()
        np.copyto(out_hat, self._forward_plan.output_array)

    def _ifft2_real(self, field_hat: np.ndarray, out: np.ndarray) -> None:
        # CPU/memory optimization: inverse transform writes through a persistent FFTW buffer.
        np.copyto(self._ifft_in, field_hat)
        self._backward_plan(normalise_idft=True)
        np.copyto(out, self._backward_plan.output_array.real)

    def _dealias_inplace(self, field_hat: np.ndarray) -> None:
        field_hat[~self.dealias] = 0.0
        field_hat[0, 0] = 0.0

    def _poisson_streamfunction_hat(self) -> None:
        # Scientific hardening: k=0 is set explicitly to enforce zero-mean streamfunction.
        np.multiply(-self.omega_hat, self.inv_k2, out=self.psi_hat)
        self.psi_hat[0, 0] = 0.0
        self._dealias_inplace(self.psi_hat)

    def _differentiate_to_real(
        self,
        field_hat: np.ndarray,
        multiplier: np.ndarray,
        out: np.ndarray,
    ) -> None:
        np.multiply(1j * multiplier, field_hat, out=self.work_hat)
        self._dealias_inplace(self.work_hat)
        self._ifft2_real(self.work_hat, out)

    def _rhs(self, omega: np.ndarray, out: np.ndarray) -> None:
        self._fft2_real(omega, self.omega_hat)
        self._dealias_inplace(self.omega_hat)
        self._poisson_streamfunction_hat()

        self._differentiate_to_real(self.psi_hat, self.ky, self.u)
        self._differentiate_to_real(self.psi_hat, self.kx, self.dpsidx)
        np.negative(self.dpsidx, out=self.v)
        np.copyto(self.dpsidy, self.u)
        self._differentiate_to_real(self.omega_hat, self.kx, self.dwdx)
        self._differentiate_to_real(self.omega_hat, self.ky, self.dwdy)

        np.multiply(-self.k2, self.omega_hat, out=self.work_hat)
        self._dealias_inplace(self.work_hat)
        self._ifft2_real(self.work_hat, self.laplace)

        # Memory optimization: build J(psi, omega) in-place through the jacobian buffer.
        np.multiply(self.dpsidx, self.dwdy, out=self.jacobian)
        np.multiply(self.dpsidy, self.dwdx, out=self.tmp)
        np.subtract(self.jacobian, self.tmp, out=self.jacobian)

        # Orszag hardening: filter the completed nonlinear product after physical multiplication.
        self._fft2_real(self.jacobian, self.work_hat)
        self._dealias_inplace(self.work_hat)
        self._ifft2_real(self.work_hat, self.jacobian)

        np.multiply(self.laplace, self.viscosity, out=out)
        np.subtract(out, self.jacobian, out=out)
        self._assert_finite("rhs", out)

    def step(self) -> SpectralAuditSample | None:
        if self.initial_enstrophy is None:
            raise RuntimeError("set_vorticity() must be called before step().")
        self._validate_cfl()

        self._rhs(self.omega, self.k1)
        np.multiply(self.k1, 0.5 * self.dt, out=self.tmp)
        np.add(self.omega, self.tmp, out=self.tmp)

        self._rhs(self.tmp, self.k2_stage)
        np.multiply(self.k2_stage, 0.5 * self.dt, out=self.tmp)
        np.add(self.omega, self.tmp, out=self.tmp)

        self._rhs(self.tmp, self.k3)
        np.multiply(self.k3, self.dt, out=self.tmp)
        np.add(self.omega, self.tmp, out=self.tmp)

        self._rhs(self.tmp, self.k4)

        # Memory optimization: RK4 accumulation reuses k buffers and tmp; no stage arrays are created.
        np.multiply(self.k2_stage, 2.0, out=self.tmp)
        np.add(self.tmp, self.k1, out=self.tmp)
        np.add(self.tmp, self.k4, out=self.tmp)
        np.multiply(self.k3, 2.0, out=self.k3)
        np.add(self.tmp, self.k3, out=self.tmp)
        np.multiply(self.tmp, self.dt / 6.0, out=self.tmp)
        np.add(self.omega, self.tmp, out=self.omega)
        self.omega -= float(np.mean(self.omega))

        self.step_index += 1
        self.time += self.dt
        self._assert_finite("vorticity", self.omega)
        self._validate_enstrophy()
        self._validate_cfl()
        return self._record_audit_sample(force_spectrum=False)

    def run(self, steps: int) -> list[SpectralAuditSample]:
        for _ in range(int(steps)):
            self.step()
        return self.audit_log

    def velocity(self, omega: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
        source = self.omega if omega is None else omega
        self._fft2_real(source, self.omega_hat)
        self._dealias_inplace(self.omega_hat)
        self._poisson_streamfunction_hat()
        self._differentiate_to_real(self.psi_hat, self.ky, self.u)
        self._differentiate_to_real(self.psi_hat, self.kx, self.v)
        np.negative(self.v, out=self.v)
        return self.u, self.v

    def energy(self, omega: np.ndarray | None = None) -> float:
        u, v = self.velocity(omega)
        return float(0.5 * np.sum(u * u + v * v) * self.cell_area)

    def enstrophy(self, omega: np.ndarray | None = None) -> float:
        source = self.omega if omega is None else omega
        return float(0.5 * np.sum(source * source) * self.cell_area)

    def energy_spectrum(self) -> dict[str, list[float]]:
        u, v = self.velocity()
        self._fft2_real(u, self.omega_hat)
        self._fft2_real(v, self.work_hat)
        energy_density = 0.5 * (np.abs(self.omega_hat) ** 2 + np.abs(self.work_hat) ** 2)
        energy_density /= float(self.nx * self.ny) ** 2
        radial_k = np.sqrt(self.k2).ravel()
        radial_energy = energy_density.ravel()
        bins = np.arange(0, int(np.max(radial_k)) + 2)
        spectrum = np.zeros(len(bins) - 1, dtype=float)
        counts = np.zeros(len(bins) - 1, dtype=int)
        indices = np.digitize(radial_k, bins) - 1
        valid = (indices >= 0) & (indices < len(spectrum))
        np.add.at(spectrum, indices[valid], radial_energy[valid])
        np.add.at(counts, indices[valid], 1)
        wavenumbers = 0.5 * (bins[:-1] + bins[1:])
        return {
            "wavenumbers": wavenumbers.tolist(),
            "energy": spectrum.tolist(),
            "counts": counts.tolist(),
        }

    def _record_audit_sample(self, *, force_spectrum: bool) -> SpectralAuditSample | None:
        with_spectrum = force_spectrum or (
            self.spectrum_interval > 0 and self.step_index % self.spectrum_interval == 0
        )
        u, v = self.velocity()
        speed = np.sqrt(u * u + v * v)
        max_velocity = float(np.max(speed))
        sample = SpectralAuditSample(
            step=self.step_index,
            time=self.time,
            energy=float(0.5 * np.sum(u * u + v * v) * self.cell_area),
            enstrophy=self.enstrophy(self.omega),
            max_velocity=max_velocity,
            cfl_number=self.dt * max_velocity / min(self.dx, self.dy),
            spectrum=self.energy_spectrum() if with_spectrum else None,
        )
        self.audit_log.append(sample)
        return sample

    def _validate_cfl(self) -> None:
        u, v = self.velocity()
        max_velocity = float(np.max(np.sqrt(u * u + v * v)))
        if max_velocity <= 0.0:
            return
        cfl_number = self.dt * max_velocity / min(self.dx, self.dy)
        if cfl_number >= self.cfl_safety:
            raise FloatingPointError(
                f"CFL violation: dt={self.dt:.6e}, max_velocity={max_velocity:.6e}, "
                f"CFL={cfl_number:.6e}, limit={self.cfl_safety:.6e}"
            )

    def _validate_enstrophy(self) -> None:
        if self.initial_enstrophy is None:
            return
        current = self.enstrophy(self.omega)
        if not np.isfinite(current):
            raise FloatingPointError("Enstrophy is NaN or Inf.")
        if current > self.enstrophy_growth_limit * max(self.initial_enstrophy, 1.0e-14):
            raise FloatingPointError(
                "Fail-closed enstrophy divergence: "
                f"{current:.6e} > {self.enstrophy_growth_limit:.3f} * "
                f"{self.initial_enstrophy:.6e}"
            )

    @staticmethod
    def _assert_finite(name: str, field: np.ndarray) -> None:
        if not np.all(np.isfinite(field)):
            raise FloatingPointError(f"{name} contains NaN or Inf values.")

    def diagnostic_state(self) -> dict[str, Any]:
        return {
            "solver": "SpectralSolver512",
            "scope": "2d_incompressible_periodic_pseudo_spectral",
            "nx": self.nx,
            "ny": self.ny,
            "length": self.length,
            "dt": self.dt,
            "viscosity": self.viscosity,
            "threads": self.threads,
            "step": self.step_index,
            "time": self.time,
            "cfl_safety": self.cfl_safety,
            "enstrophy_growth_limit": self.enstrophy_growth_limit,
            "dealiasing": "two_thirds_orszag",
            "scientific_acceptance": "human_review_required",
            "limitations": [
                "2d_periodic_solver_only",
                "not_a_3d_result",
                "not_a_millennium_problem_solution",
                "not_a_mathematical_proof",
            ],
        }
