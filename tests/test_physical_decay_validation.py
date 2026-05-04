from __future__ import annotations

import json
from pathlib import Path

from navier_stokes_research.cli import build_parser
from navier_stokes_research.physical_decay import (
    _non_increasing_with_tolerance,
    run_physical_decay_validation,
)


def test_cli_parser_supports_physical_decay_validation_flag() -> None:
    parser = build_parser()
    args = parser.parse_args(["--physical-decay-validation"])
    assert args.physical_decay_validation is True


def test_non_increasing_with_tolerance_passes_with_small_numerical_drift() -> None:
    assert _non_increasing_with_tolerance(1.0, 1.0 + 5e-11, relative_tolerance=1e-10)


def test_non_increasing_with_tolerance_fails_when_growth_exceeds_tolerance() -> None:
    assert not _non_increasing_with_tolerance(1.0, 1.0 + 5e-9, relative_tolerance=1e-10)


def test_physical_decay_validation_outputs_and_statuses(tmp_path: Path) -> None:
    result = run_physical_decay_validation(base_output_dir=str(tmp_path / "benchmarks"))
    json_path = Path(result["physical_decay_validation_path"])
    metrics_csv = Path(result["metrics_csv_path"])
    validation_report = Path(result["validation_report_path"])

    assert json_path.exists()
    assert metrics_csv.exists()
    assert validation_report.exists()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["study_name"] == "physical_decay_2d"
    assert payload["acceptance_statuses"]["runtime_execution"] in {"passed", "warning", "failed"}
    assert payload["acceptance_statuses"]["physical_decay_status"] in {"passed", "warning", "failed"}
    assert payload["acceptance_statuses"]["scientific_acceptance"] == "human_review_required"


def test_physical_decay_validation_expected_deterministic_pass(tmp_path: Path) -> None:
    result = run_physical_decay_validation(base_output_dir=str(tmp_path / "benchmarks"))
    payload = json.loads(
        Path(result["physical_decay_validation_path"]).read_text(encoding="utf-8")
    )
    assert payload["acceptance_statuses"]["physical_decay_status"] == "passed"
    assert payload["checks"]["finite_metrics"]["ok"] is True
    assert payload["checks"]["energy_non_increasing"]["ok"] is True
    assert payload["checks"]["enstrophy_non_increasing"]["ok"] is True
    assert payload["checks"]["cfl_margin_positive"]["ok"] is True
    assert payload["checks"]["diffusion_margin_positive"]["ok"] is True
