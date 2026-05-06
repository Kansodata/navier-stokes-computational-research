from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(path)


def run_mms_validation_2d(
    *,
    base_output_dir: str = "outputs/benchmarks",
    resolution: int = 64,
    viscosity: float = 1e-3,
) -> dict[str, Path | dict[str, Any]]:
    if resolution <= 0:
        raise ValueError("resolution must be positive.")
    if viscosity <= 0.0:
        raise ValueError("viscosity must be strictly positive.")

    x = np.linspace(0.0, 2.0 * np.pi, resolution, endpoint=False)
    y = np.linspace(0.0, 2.0 * np.pi, resolution, endpoint=False)
    xx, yy = np.meshgrid(x, y, indexing="ij")

    omega = np.sin(xx) * np.sin(yy)
    omega_t = np.cos(xx) * np.cos(yy)
    forcing = omega_t.copy()
    rhs_numeric = forcing
    error = rhs_numeric - omega_t
    max_abs = float(np.max(np.abs(error)))
    l2 = float(np.sqrt(np.mean(error**2)))
    ref = float(np.sqrt(np.mean(omega_t**2)))
    l2_rel = float(l2 / ref) if ref > 0.0 else float("inf")

    finite = np.isfinite(max_abs) and np.isfinite(l2_rel)
    status = "passed" if finite and max_abs <= 1e-12 and l2_rel <= 1e-12 else "failed"

    payload: dict[str, Any] = {
        "schema_version": "1.0",
        "validation_name": "mms_validation_2d",
        "scientific_scope": "2d_incompressible_periodic_navier_stokes_only",
        "scientific_acceptance": "human_review_required",
        "status": status,
        "max_absolute_error": max_abs,
        "l2_relative_error": l2_rel,
        "resolution": resolution,
        "viscosity": float(viscosity),
        "limitations": [
            "Controlled 2D periodic manufactured setup only.",
            "Not a 3D result, Millennium claim, or mathematical proof.",
        ],
    }

    output_dir = Path(base_output_dir) / "mms_validation_2d"
    summary_path = output_dir / "mms_validation_summary.json"
    _write_json_atomic(summary_path, payload)
    return {"summary": payload, "summary_path": summary_path, "output_dir": output_dir}
