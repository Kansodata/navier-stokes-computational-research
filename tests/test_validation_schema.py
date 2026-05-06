from __future__ import annotations

import re

import pytest

from navier_stokes_research.validation_schema import (
    CANONICAL_SOLVER_SCOPE,
    build_validation_result,
)


def test_build_validation_result_generates_required_fields() -> None:
    payload = build_validation_result(
        validation_id="unit_test_validation",
        validation_type="diagnostic",
        status="passed",
        claim_scope="diagnostic_only",
    )
    for key in (
        "schema_version",
        "validation_id",
        "validation_type",
        "status",
        "generated_at_utc",
        "solver_scope",
        "claim_scope",
        "parameters",
        "metrics",
        "thresholds",
        "artifacts",
        "limitations",
        "notes",
    ):
        assert key in payload
    assert payload["solver_scope"] == CANONICAL_SOLVER_SCOPE
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", payload["generated_at_utc"])


def test_build_validation_result_fails_closed_on_invalid_status() -> None:
    with pytest.raises(ValueError, match="status must be one of"):
        build_validation_result(
            validation_id="unit_test_validation",
            validation_type="diagnostic",
            status="invalid_status",
            claim_scope="diagnostic_only",
        )


def test_build_validation_result_fails_closed_on_invalid_validation_type() -> None:
    with pytest.raises(ValueError, match="validation_type must be one of"):
        build_validation_result(
            validation_id="unit_test_validation",
            validation_type="invalid_type",
            status="passed",
            claim_scope="diagnostic_only",
        )


def test_build_validation_result_fails_closed_on_unsafe_claim_scope() -> None:
    with pytest.raises(ValueError, match="forbidden term"):
        build_validation_result(
            validation_id="unit_test_validation",
            validation_type="diagnostic",
            status="passed",
            claim_scope="3d_ready",
        )
