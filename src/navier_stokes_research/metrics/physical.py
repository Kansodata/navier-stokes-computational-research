from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass

import numpy as np

_ALLOWED_DEALIASING_METHODS = {"none", "two_thirds", "spectral_filter", "unknown"}


def _as_2d_finite_array(name: str, values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim != 2:
        raise ValueError(f"{name} must be a 2D array.")
    if array.size == 0:
        raise ValueError(f"{name} must be non-empty.")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains NaN or Inf values.")
    return array


def _as_positive_float(name: str, value: float) -> float:
    number = float(value)
    if not np.isfinite(number):
        raise ValueError(f"{name} must be finite.")
    if number <= 0.0:
        raise ValueError(f"{name} must be > 0.")
    return number


def _as_non_negative_float(name: str, value: float) -> float:
    number = float(value)
    if not np.isfinite(number):
        raise ValueError(f"{name} must be finite.")
    if number < 0.0:
        raise ValueError(f"{name} must be >= 0.")
    return number


def total_kinetic_energy(u: np.ndarray, v: np.ndarray, dx: float, dy: float) -> float:
    u_field = _as_2d_finite_array("u", u)
    v_field = _as_2d_finite_array("v", v)
    if u_field.shape != v_field.shape:
        raise ValueError("u and v must have identical shape.")
    dx_value = _as_positive_float("dx", dx)
    dy_value = _as_positive_float("dy", dy)
    return float(0.5 * np.sum(u_field**2 + v_field**2) * dx_value * dy_value)


def total_enstrophy(vorticity: np.ndarray, dx: float, dy: float) -> float:
    omega_field = _as_2d_finite_array("vorticity", vorticity)
    dx_value = _as_positive_float("dx", dx)
    dy_value = _as_positive_float("dy", dy)
    return float(0.5 * np.sum(omega_field**2) * dx_value * dy_value)


@dataclass(frozen=True)
class PhysicalDiagnosticsPayload:
    energy: float
    enstrophy: float
    viscosity: float
    resolution: dict[str, int]
    dt: float
    t: float
    initial_condition: str
    dealiasing_method: str

    def to_dict(self) -> dict[str, float | str | dict[str, int]]:
        return asdict(self)


def build_physical_diagnostics_payload(
    *,
    energy: float,
    enstrophy: float,
    viscosity: float,
    nx: int,
    ny: int,
    dt: float,
    t: float,
    initial_condition: str,
    dealiasing_method: str,
) -> dict[str, float | str | dict[str, int]]:
    if not isinstance(initial_condition, str) or not initial_condition.strip():
        raise ValueError("initial_condition must be a non-empty string.")
    if dealiasing_method not in _ALLOWED_DEALIASING_METHODS:
        allowed = ", ".join(sorted(_ALLOWED_DEALIASING_METHODS))
        raise ValueError(f"dealiasing_method must be one of: {allowed}.")
    if not isinstance(nx, int) or nx <= 0:
        raise ValueError("nx must be a positive integer.")
    if not isinstance(ny, int) or ny <= 0:
        raise ValueError("ny must be a positive integer.")

    payload = PhysicalDiagnosticsPayload(
        energy=_as_non_negative_float("energy", energy),
        enstrophy=_as_non_negative_float("enstrophy", enstrophy),
        viscosity=_as_non_negative_float("viscosity", viscosity),
        resolution={"nx": nx, "ny": ny},
        dt=_as_positive_float("dt", dt),
        t=_as_non_negative_float("t", t),
        initial_condition=initial_condition,
        dealiasing_method=dealiasing_method,
    )
    return payload.to_dict()


def ensure_required_physical_diagnostics(payload: Mapping[str, object]) -> None:
    required_keys = {
        "energy",
        "enstrophy",
        "viscosity",
        "resolution",
        "dt",
        "t",
        "initial_condition",
        "dealiasing_method",
    }
    missing = sorted(required_keys.difference(payload.keys()))
    if missing:
        raise ValueError(f"Missing required diagnostics keys: {', '.join(missing)}")
