from __future__ import annotations

import json
from pathlib import Path

from navier_stokes_research.cli import build_parser
from navier_stokes_research.stress_validation import (
    SCENARIO_STATUSES,
    StressScenarioSpec,
    _run_single_scenario,
    run_stress_validation_2d,
)


def test_cli_parser_supports_stress_validation_2d_flag() -> None:
    parser = build_parser()
    args = parser.parse_args(["--stress-validation-2d"])
    assert args.stress_validation_2d is True


def test_cfl_violation_is_expected_fail_closed(tmp_path: Path) -> None:
    scenario = StressScenarioSpec(
        name="cfl_violation_unit_test",
        steps=2,
        target_initial_cfl=0.95,
        expected_failure_reason="CFL violation",
    )
    result = _run_single_scenario(scenario, tmp_path / "stress")

    assert result["status"] == "expected_fail_closed"
    assert result["error"]["controlled"] is True
    assert "CFL violation" in result["error"]["message"]


def test_baseline_control_scenario_produces_finite_metrics(tmp_path: Path) -> None:
    scenario = StressScenarioSpec(
        name="baseline_control_unit_test",
        steps=4,
        target_initial_cfl=0.25,
    )
    result = _run_single_scenario(scenario, tmp_path / "stress")

    assert result["status"] in {"passed", "warning"}
    assert result["metrics_summary"]["finite_metrics"] is True
    assert result["metrics_summary"]["samples"] == 5
    assert result["stability_summary"]["cfl_margin_min"] > 0.0
    assert result["spectral_evidence"]["status"] == "available"
    assert 0.0 <= result["spectral_evidence"]["high_wavenumber_energy_fraction"] <= 1.0


def test_stress_validation_summary_schema_and_statuses(tmp_path: Path) -> None:
    result = run_stress_validation_2d(base_output_dir=str(tmp_path / "benchmarks"))
    summary_path = Path(result["summary_path"])
    output_dir = Path(result["output_dir"])

    assert summary_path.exists()
    assert output_dir.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["study_name"] == "stress_validation_2d"
    assert "created_at_utc" in payload
    assert "scenarios" in payload
    assert "summary" in payload
    assert "warnings" in payload
    assert "acceptance_statuses" in payload

    scenario_names = {scenario["name"] for scenario in payload["scenarios"]}
    assert {
        "baseline_control",
        "near_cfl_limit",
        "cfl_violation_expected_fail",
        "low_viscosity",
        "high_amplitude",
        "coarse_grid",
        "multiple_seeds",
        "spectral_high_k_observation",
    }.issubset(scenario_names)

    statuses = {scenario["status"] for scenario in payload["scenarios"]}
    assert statuses.issubset(SCENARIO_STATUSES)
    assert payload["acceptance_statuses"]["runtime_execution"] in {"passed", "failed"}
    assert payload["acceptance_statuses"]["stress_validation_status"] in {
        "passed",
        "warning",
        "failed",
    }
    assert payload["acceptance_statuses"]["scientific_acceptance"] == "human_review_required"

    expected_fail = next(
        scenario
        for scenario in payload["scenarios"]
        if scenario["name"] == "cfl_violation_expected_fail"
    )
    assert expected_fail["status"] == "expected_fail_closed"
    assert expected_fail["error"]["controlled"] is True

    spectral = next(
        scenario
        for scenario in payload["scenarios"]
        if scenario["name"] == "spectral_high_k_observation"
    )
    assert spectral["spectral_evidence"]["status"] == "available"
    assert spectral["spectral_evidence"]["interpretation"] == "diagnostic_only_not_hard_gate"
