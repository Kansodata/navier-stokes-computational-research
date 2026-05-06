from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

ALLOWED_VALIDATION_TYPES = {"verification", "validation", "diagnostic"}
ALLOWED_STATUSES = {"passed", "failed", "warning", "skipped"}
SCHEMA_VERSION = "1.0"
CANONICAL_SOLVER_SCOPE = "2d_incompressible_periodic_pseudo_spectral"

_FORBIDDEN_CLAIM_TERMS = ("3d", "millennium", "proof", "formal_resolution")


def _generated_at_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _validate_validation_type(value: str) -> None:
    if value not in ALLOWED_VALIDATION_TYPES:
        raise ValueError(
            f"validation_type must be one of {sorted(ALLOWED_VALIDATION_TYPES)}, got: {value}"
        )


def _validate_status(value: str) -> None:
    if value not in ALLOWED_STATUSES:
        raise ValueError(f"status must be one of {sorted(ALLOWED_STATUSES)}, got: {value}")


def _validate_claim_scope(value: str) -> None:
    lowered = value.lower()
    for term in _FORBIDDEN_CLAIM_TERMS:
        if term in lowered:
            raise ValueError(f"claim_scope contains forbidden term '{term}': {value}")


def build_validation_result(
    *,
    validation_id: str,
    validation_type: str,
    status: str,
    claim_scope: str,
    parameters: dict[str, Any] | None = None,
    metrics: dict[str, Any] | None = None,
    thresholds: dict[str, Any] | None = None,
    artifacts: dict[str, Any] | None = None,
    limitations: list[str] | None = None,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    _validate_validation_type(validation_type)
    _validate_status(status)
    _validate_claim_scope(claim_scope)

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "validation_id": validation_id,
        "validation_type": validation_type,
        "status": status,
        "generated_at_utc": _generated_at_utc(),
        "solver_scope": CANONICAL_SOLVER_SCOPE,
        "claim_scope": claim_scope,
        "parameters": parameters or {},
        "metrics": metrics or {},
        "thresholds": thresholds or {},
        "artifacts": artifacts or {},
        "limitations": limitations or [],
        "notes": notes or [],
    }
    return payload
