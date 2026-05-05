from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from navier_stokes_research.physical_decay import run_physical_decay_validation
from navier_stokes_research.stress_validation import run_stress_validation_2d
from navier_stokes_research.taylor_green import run_taylor_green_validation

EXTERNAL_VALIDATION_STUDY_NAME = "external_reference_validation_2d"
ENERGY_ENSTROPHY_RATIO_LIMIT = 1.1
TAYLOR_GREEN_ROUNDOFF_FLOOR = 1e-12


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_taylor_green_payload(base_output_dir: str) -> tuple[dict[str, Any], Path]:
    path = Path(base_output_dir) / "taylor_green_2d" / "taylor_green_validation.json"
    if path.exists():
        return _load_json(path), path
    result = run_taylor_green_validation(base_output_dir=base_output_dir)
    report_path = Path(result["report_path"])
    return _load_json(report_path), report_path


def _ensure_physical_decay_payload(base_output_dir: str) -> tuple[dict[str, Any], Path]:
    path = Path(base_output_dir) / "physical_decay_2d" / "physical_decay_validation.json"
    if path.exists():
        return _load_json(path), path
    result = run_physical_decay_validation(base_output_dir=base_output_dir)
    report_path = Path(result["physical_decay_validation_path"])
    return _load_json(report_path), report_path


def _ensure_stress_validation_payload(base_output_dir: str) -> tuple[dict[str, Any], Path]:
    path = Path(base_output_dir) / "stress_validation_2d" / "stress_validation_summary.json"
    if path.exists():
        return _load_json(path), path
    result = run_stress_validation_2d(base_output_dir=base_output_dir)
    report_path = Path(result["summary_path"])
    return _load_json(report_path), report_path


def _status_from_check(ok: bool, fallback_failed: bool = False, fail_status: str = "warning") -> str:
    if fallback_failed:
        return "failed"
    return "passed" if ok else fail_status


def run_external_reference_validation_2d(
    base_output_dir: str = "outputs/benchmarks",
) -> dict[str, Path]:
    output_dir = Path(base_output_dir) / EXTERNAL_VALIDATION_STUDY_NAME
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "external_reference_validation_summary.json"

    warnings: list[str] = []
    hard_failures: list[str] = []

    taylor_payload, taylor_path = _ensure_taylor_green_payload(base_output_dir)
    errors = taylor_payload.get("errors", {})
    error_values = [
        float(errors[key])
        for key in ("l2", "linf", "relative")
        if isinstance(errors.get(key), (float, int))
    ]
    taylor_roundoff_ok = bool(error_values) and max(error_values) <= TAYLOR_GREEN_ROUNDOFF_FLOOR
    taylor_status = "passed_roundoff_floor" if taylor_roundoff_ok else "warning"
    if not taylor_roundoff_ok:
        warnings.append("taylor_green_not_roundoff_floor")

    decay_payload, decay_path = _ensure_physical_decay_payload(base_output_dir)
    metrics_summary = decay_payload.get("metrics_summary", {})
    initial_energy = float(metrics_summary.get("initial_energy", 0.0))
    final_energy = float(metrics_summary.get("final_energy", 0.0))
    initial_enstrophy = float(metrics_summary.get("initial_enstrophy", 0.0))
    final_enstrophy = float(metrics_summary.get("final_enstrophy", 0.0))

    energy_ratio = float("inf") if initial_energy <= 0.0 else final_energy / initial_energy
    enstrophy_ratio = (
        float("inf") if initial_enstrophy <= 0.0 else final_enstrophy / initial_enstrophy
    )
    decay_ok = (
        energy_ratio <= ENERGY_ENSTROPHY_RATIO_LIMIT
        and enstrophy_ratio <= ENERGY_ENSTROPHY_RATIO_LIMIT
    )
    decay_status = _status_from_check(decay_ok)
    if not decay_ok:
        warnings.append("energy_or_enstrophy_ratio_above_limit")

    spectral_source = decay_payload.get("spectral_evidence", {})
    spectral_status = "diagnostic_only"

    stress_payload, stress_path = _ensure_stress_validation_payload(base_output_dir)
    non_expected_failures = stress_payload.get("summary", {}).get("non_expected_failures", [])
    unexpected_failures = [str(item) for item in non_expected_failures]
    stress_ok = len(unexpected_failures) == 0
    stress_status = _status_from_check(stress_ok, fail_status="failed")
    if not stress_ok:
        hard_failures.append("stress_validation_unexpected_failures")
        warnings.append("unexpected_stress_failures_present")

    if not stress_ok:
        overall_status = "failed"
    elif taylor_status == "warning" or decay_status == "warning":
        overall_status = "warning"
    else:
        overall_status = "passed"

    payload = {
        "study_name": EXTERNAL_VALIDATION_STUDY_NAME,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "solver": "2d_incompressible_periodic_pseudospectral_vorticity_streamfunction",
            "external_references_only": True,
        },
        "checks": {
            "taylor_green_2d": {
                "status": taylor_status,
                "roundoff_floor_threshold": TAYLOR_GREEN_ROUNDOFF_FLOOR,
                "errors": {
                    "l2": errors.get("l2"),
                    "linf": errors.get("linf"),
                    "relative": errors.get("relative"),
                },
                "artifact": str(taylor_path),
            },
            "energy_enstrophy_decay": {
                "status": decay_status,
                "ratio_limit": ENERGY_ENSTROPHY_RATIO_LIMIT,
                "energy_ratio": energy_ratio,
                "enstrophy_ratio": enstrophy_ratio,
                "artifact": str(decay_path),
            },
            "spectral_consistency": {
                "status": spectral_status,
                "interpretation": "diagnostic_only_not_hard_gate",
                "high_wavenumber_energy_fraction": spectral_source.get(
                    "high_wavenumber_energy_fraction"
                ),
                "artifact": spectral_source.get("artifact", str(decay_path)),
            },
            "stress_validation": {
                "status": stress_status,
                "unexpected_failures": unexpected_failures,
                "artifact": str(stress_path),
            },
        },
        "overall_status": overall_status,
        "hard_failures": hard_failures,
        "warnings": warnings,
        "scientific_acceptance": {
            "status": "human_review_required",
            "reasons": [
                "external_reference_2d_scope_only",
                "diagnostic_signals_not_formal_proof",
                "not_a_3d_existence_or_smoothness_proof",
            ],
        },
    }
    summary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {"output_dir": output_dir, "summary_path": summary_path}
