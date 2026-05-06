from __future__ import annotations

import json
from pathlib import Path

from navier_stokes_research.cli import build_parser
from navier_stokes_research.resolution_sensitivity_study import (
    run_resolution_sensitivity_study_2d,
)
from navier_stokes_research.validation_schema import CANONICAL_SOLVER_SCOPE


def test_cli_parser_supports_resolution_sensitivity_flag() -> None:
    parser = build_parser()
    args = parser.parse_args(["--resolution-sensitivity-study-2d"])
    assert args.resolution_sensitivity_study_2d is True


def test_resolution_sensitivity_study_generates_schema_artifact(tmp_path: Path) -> None:
    result = run_resolution_sensitivity_study_2d(
        base_output_dir=str(tmp_path / "benchmarks"),
        resolutions=(24, 32),
        final_time=0.004,
    )
    summary_path = Path(result["summary_path"])
    assert summary_path.exists()
    payload = json.loads(summary_path.read_text(encoding="utf-8"))

    assert payload["schema_version"] == "1.0"
    assert payload["validation_id"] == "resolution_sensitivity_2d"
    assert payload["validation_type"] == "diagnostic"
    assert payload["solver_scope"] == CANONICAL_SOLVER_SCOPE
    assert payload["claim_scope"] == "diagnostic_only"
    assert payload["status"] in {"passed", "warning", "failed"}
    assert payload["scientific_acceptance"] == "human_review_required"
    assert payload["summary"]["unexpected_failures"] == []
    assert len(payload["resolutions"]) == 2
    for run in payload["resolutions"]:
        assert run["status"] in {"passed", "warning", "failed"}
        assert run["orszag_component_cutoff_k"] == run["resolution"] // 3
        assert "direct_cascade_slope_relative_error" in run
        assert "inverse_cascade_slope_relative_error" in run
    assert payload["recommendation"]["status"] in {"candidate_identified", "not_identified"}


def test_resolution_sensitivity_rejects_unsafe_resolution(tmp_path: Path) -> None:
    try:
        run_resolution_sensitivity_study_2d(
            base_output_dir=str(tmp_path / "benchmarks"),
            resolutions=(8,),
            final_time=0.004,
        )
    except ValueError as exc:
        assert "N >= 16" in str(exc)
    else:
        raise AssertionError("Expected fail-closed ValueError for too-small resolution.")
