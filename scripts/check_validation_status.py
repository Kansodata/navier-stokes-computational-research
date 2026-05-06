from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


ROOT = Path("outputs") / "benchmarks"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing expected artifact: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON artifact: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"Invalid JSON root type for {path}; expected object.")
    return payload


def _require_field(obj: dict[str, Any], field: str, context: str) -> Any:
    if field not in obj:
        raise RuntimeError(f"Missing required field '{field}' in {context}.")
    return obj[field]


def _is_bad_status(value: str) -> bool:
    lowered = value.lower()
    if lowered in {"failed", "error", "invalid", "unknown"}:
        return True
    return lowered.startswith("fail")


def _assert_status_not_failed(value: Any, context: str) -> None:
    if not isinstance(value, str):
        raise RuntimeError(f"Status field in {context} must be a string.")
    if _is_bad_status(value):
        raise RuntimeError(f"Fail-closed status in {context}: {value}")


def _assert_finite_number(value: Any, context: str) -> None:
    if not isinstance(value, (float, int)):
        raise RuntimeError(f"Expected numeric field in {context}, got {type(value).__name__}.")
    if not math.isfinite(float(value)):
        raise RuntimeError(f"Non-finite metric in {context}: {value}")


def _check_taylor_green() -> None:
    payload = _load_json(ROOT / "taylor_green_2d" / "taylor_green_validation.json")
    _assert_status_not_failed(_require_field(payload, "execution_status", "taylor_green"), "taylor_green.execution_status")
    _assert_status_not_failed(_require_field(payload, "accuracy_status", "taylor_green"), "taylor_green.accuracy_status")
    errors = _require_field(payload, "errors", "taylor_green")
    if not isinstance(errors, dict):
        raise RuntimeError("taylor_green.errors must be an object.")
    _assert_finite_number(_require_field(errors, "l2", "taylor_green.errors"), "taylor_green.errors.l2")
    _assert_finite_number(_require_field(errors, "linf", "taylor_green.errors"), "taylor_green.errors.linf")
    relative = _require_field(errors, "relative", "taylor_green.errors")
    if relative is not None:
        _assert_finite_number(relative, "taylor_green.errors.relative")


def _check_taylor_green_convergence() -> None:
    payload = _load_json(ROOT / "taylor_green_convergence_2d" / "taylor_green_convergence_summary.json")
    acceptance = _require_field(payload, "acceptance_statuses", "taylor_green_convergence")
    if not isinstance(acceptance, dict):
        raise RuntimeError("taylor_green_convergence.acceptance_statuses must be an object.")
    _assert_status_not_failed(
        _require_field(acceptance, "runtime_execution", "taylor_green_convergence.acceptance_statuses"),
        "taylor_green_convergence.runtime_execution",
    )
    _assert_status_not_failed(
        _require_field(acceptance, "formal_error_convergence", "taylor_green_convergence.acceptance_statuses"),
        "taylor_green_convergence.formal_error_convergence",
    )
    runs = _require_field(payload, "runs", "taylor_green_convergence")
    if not isinstance(runs, list) or not runs:
        raise RuntimeError("taylor_green_convergence.runs must be a non-empty list.")
    for idx, run in enumerate(runs):
        if not isinstance(run, dict):
            raise RuntimeError(f"taylor_green_convergence.runs[{idx}] must be an object.")
        _assert_status_not_failed(run.get("execution_status"), f"taylor_green_convergence.runs[{idx}].execution_status")
        _assert_status_not_failed(run.get("accuracy_status"), f"taylor_green_convergence.runs[{idx}].accuracy_status")


def _check_physical_decay() -> None:
    payload = _load_json(ROOT / "physical_decay_2d" / "physical_decay_validation.json")
    acceptance = _require_field(payload, "acceptance_statuses", "physical_decay")
    if not isinstance(acceptance, dict):
        raise RuntimeError("physical_decay.acceptance_statuses must be an object.")
    _assert_status_not_failed(
        _require_field(acceptance, "runtime_execution", "physical_decay.acceptance_statuses"),
        "physical_decay.runtime_execution",
    )
    _assert_status_not_failed(
        _require_field(acceptance, "physical_decay_status", "physical_decay.acceptance_statuses"),
        "physical_decay.physical_decay_status",
    )
    checks = _require_field(payload, "checks", "physical_decay")
    if not isinstance(checks, dict) or not checks:
        raise RuntimeError("physical_decay.checks must be a non-empty object.")
    for name, item in checks.items():
        if not isinstance(item, dict):
            raise RuntimeError(f"physical_decay.checks.{name} must be an object.")
        ok = _require_field(item, "ok", f"physical_decay.checks.{name}")
        if not isinstance(ok, bool):
            raise RuntimeError(f"physical_decay.checks.{name}.ok must be boolean.")
        if not ok:
            raise RuntimeError(f"Fail-closed check in physical_decay.checks.{name}.ok = false")
    metrics = _require_field(payload, "metrics_summary", "physical_decay")
    if not isinstance(metrics, dict):
        raise RuntimeError("physical_decay.metrics_summary must be an object.")
    for key in ("initial_energy", "final_energy", "initial_enstrophy", "final_enstrophy", "cfl_peak"):
        _assert_finite_number(_require_field(metrics, key, "physical_decay.metrics_summary"), f"physical_decay.metrics_summary.{key}")

    spectral = _require_field(payload, "spectral_evidence", "physical_decay")
    if not isinstance(spectral, dict):
        raise RuntimeError("physical_decay.spectral_evidence must be an object.")
    _assert_status_not_failed(_require_field(spectral, "status", "physical_decay.spectral_evidence"), "physical_decay.spectral_evidence.status")
    _assert_finite_number(
        _require_field(spectral, "high_wavenumber_energy_fraction", "physical_decay.spectral_evidence"),
        "physical_decay.spectral_evidence.high_wavenumber_energy_fraction",
    )


def _check_stress_validation() -> None:
    payload = _load_json(ROOT / "stress_validation_2d" / "stress_validation_summary.json")
    acceptance = _require_field(payload, "acceptance_statuses", "stress_validation")
    if not isinstance(acceptance, dict):
        raise RuntimeError("stress_validation.acceptance_statuses must be an object.")
    _assert_status_not_failed(
        _require_field(acceptance, "runtime_execution", "stress_validation.acceptance_statuses"),
        "stress_validation.runtime_execution",
    )
    _assert_status_not_failed(
        _require_field(acceptance, "stress_validation_status", "stress_validation.acceptance_statuses"),
        "stress_validation.stress_validation_status",
    )
    summary = _require_field(payload, "summary", "stress_validation")
    if not isinstance(summary, dict):
        raise RuntimeError("stress_validation.summary must be an object.")
    non_expected = _require_field(summary, "non_expected_failures", "stress_validation.summary")
    if not isinstance(non_expected, list):
        raise RuntimeError("stress_validation.summary.non_expected_failures must be a list.")
    if non_expected:
        raise RuntimeError(f"stress_validation.summary.non_expected_failures must be empty, got: {non_expected}")


def _check_time_refinement() -> None:
    payload = _load_json(ROOT / "time_refinement_2d" / "time_refinement_summary.json")
    summary = _require_field(payload, "summary", "time_refinement")
    if not isinstance(summary, dict):
        raise RuntimeError("time_refinement.summary must be an object.")
    _assert_status_not_failed(_require_field(summary, "runtime_execution", "time_refinement.summary"), "time_refinement.runtime_execution")
    _assert_status_not_failed(_require_field(summary, "time_refinement_status", "time_refinement.summary"), "time_refinement.time_refinement_status")
    unexpected = _require_field(summary, "unexpected_failures", "time_refinement.summary")
    if not isinstance(unexpected, list):
        raise RuntimeError("time_refinement.summary.unexpected_failures must be a list.")
    if unexpected:
        raise RuntimeError(f"time_refinement.summary.unexpected_failures must be empty, got: {unexpected}")

    dt_levels = _require_field(payload, "dt_levels", "time_refinement")
    if not isinstance(dt_levels, list) or not dt_levels:
        raise RuntimeError("time_refinement.dt_levels must be a non-empty list.")
    for idx, level in enumerate(dt_levels):
        if not isinstance(level, dict):
            raise RuntimeError(f"time_refinement.dt_levels[{idx}] must be an object.")
        _assert_status_not_failed(_require_field(level, "status", f"time_refinement.dt_levels[{idx}]"), f"time_refinement.dt_levels[{idx}].status")
        for key in ("final_energy", "final_enstrophy", "final_max_velocity", "cfl_peak"):
            value = _require_field(level, key, f"time_refinement.dt_levels[{idx}]")
            if value is None:
                raise RuntimeError(f"time_refinement.dt_levels[{idx}].{key} must not be null.")
            _assert_finite_number(value, f"time_refinement.dt_levels[{idx}].{key}")


def _check_multi_resolution_energy_enstrophy() -> None:
    payload = _load_json(
        ROOT
        / "multi_resolution_energy_enstrophy_2d"
        / "multi_resolution_energy_enstrophy_summary.json"
    )
    acceptance = _require_field(payload, "acceptance_statuses", "multi_resolution_energy_enstrophy")
    if not isinstance(acceptance, dict):
        raise RuntimeError("multi_resolution_energy_enstrophy.acceptance_statuses must be an object.")

    # Normalized schema contract checks
    if _require_field(payload, "schema_version", "multi_resolution_energy_enstrophy") != "1.0":
        raise RuntimeError("multi_resolution_energy_enstrophy.schema_version must be '1.0'.")
    if (
        _require_field(payload, "validation_type", "multi_resolution_energy_enstrophy")
        != "diagnostic"
    ):
        raise RuntimeError(
            "multi_resolution_energy_enstrophy.validation_type must be 'diagnostic'."
        )
    _assert_status_not_failed(
        _require_field(payload, "status", "multi_resolution_energy_enstrophy"),
        "multi_resolution_energy_enstrophy.status",
    )
    if (
        _require_field(payload, "solver_scope", "multi_resolution_energy_enstrophy")
        != "2d_incompressible_periodic_pseudo_spectral"
    ):
        raise RuntimeError(
            "multi_resolution_energy_enstrophy.solver_scope must be "
            "'2d_incompressible_periodic_pseudo_spectral'."
        )
    claim_scope = _require_field(payload, "claim_scope", "multi_resolution_energy_enstrophy")
    if not isinstance(claim_scope, str):
        raise RuntimeError("multi_resolution_energy_enstrophy.claim_scope must be a string.")
    for forbidden in ("3d", "millennium", "proof", "formal_resolution"):
        if forbidden in claim_scope.lower():
            raise RuntimeError(
                "multi_resolution_energy_enstrophy.claim_scope contains forbidden token: "
                f"{forbidden}"
            )
    for container_key in ("parameters", "metrics", "thresholds", "artifacts"):
        container = _require_field(payload, container_key, "multi_resolution_energy_enstrophy")
        if not isinstance(container, dict):
            raise RuntimeError(
                f"multi_resolution_energy_enstrophy.{container_key} must be an object."
            )
    for list_key in ("limitations", "notes"):
        value = _require_field(payload, list_key, "multi_resolution_energy_enstrophy")
        if not isinstance(value, list):
            raise RuntimeError(f"multi_resolution_energy_enstrophy.{list_key} must be a list.")
    _assert_status_not_failed(
        _require_field(
            acceptance,
            "runtime_execution",
            "multi_resolution_energy_enstrophy.acceptance_statuses",
        ),
        "multi_resolution_energy_enstrophy.runtime_execution",
    )
    _assert_status_not_failed(
        _require_field(
            acceptance,
            "energy_enstrophy_regression_status",
            "multi_resolution_energy_enstrophy.acceptance_statuses",
        ),
        "multi_resolution_energy_enstrophy.energy_enstrophy_regression_status",
    )

    resolutions = _require_field(payload, "resolutions", "multi_resolution_energy_enstrophy")
    if not isinstance(resolutions, list) or not resolutions:
        raise RuntimeError("multi_resolution_energy_enstrophy.resolutions must be a non-empty list.")

    for idx, run in enumerate(resolutions):
        if not isinstance(run, dict):
            raise RuntimeError(f"multi_resolution_energy_enstrophy.resolutions[{idx}] must be an object.")
        _assert_status_not_failed(
            _require_field(run, "status", f"multi_resolution_energy_enstrophy.resolutions[{idx}]"),
            f"multi_resolution_energy_enstrophy.resolutions[{idx}].status",
        )
        for key in (
            "initial_energy",
            "final_energy",
            "initial_enstrophy",
            "final_enstrophy",
            "energy_ratio",
            "enstrophy_ratio",
            "cfl_peak",
            "diffusion_margin",
        ):
            _assert_finite_number(
                _require_field(
                    run, key, f"multi_resolution_energy_enstrophy.resolutions[{idx}]"
                ),
                f"multi_resolution_energy_enstrophy.resolutions[{idx}].{key}",
            )

    summary = _require_field(payload, "summary", "multi_resolution_energy_enstrophy")
    if not isinstance(summary, dict):
        raise RuntimeError("multi_resolution_energy_enstrophy.summary must be an object.")
    unexpected = _require_field(
        summary,
        "unexpected_failures",
        "multi_resolution_energy_enstrophy.summary",
    )
    if not isinstance(unexpected, list):
        raise RuntimeError(
            "multi_resolution_energy_enstrophy.summary.unexpected_failures must be a list."
        )
    if unexpected:
        raise RuntimeError(
            "multi_resolution_energy_enstrophy.summary.unexpected_failures must be empty, "
            f"got: {unexpected}"
        )


def main() -> None:
    _check_taylor_green()
    _check_taylor_green_convergence()
    _check_physical_decay()
    _check_stress_validation()
    _check_time_refinement()
    _check_multi_resolution_energy_enstrophy()
    print("Validation artifact status check passed.")


if __name__ == "__main__":
    main()
