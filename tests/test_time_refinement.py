from __future__ import annotations

import json
from pathlib import Path

from navier_stokes_research.cli import build_parser
from navier_stokes_research.time_refinement import run_time_refinement_validation_2d


def test_cli_parser_supports_time_refinement_2d_flag() -> None:
    parser = build_parser()
    args = parser.parse_args(["--time-refinement-2d"])
    assert args.time_refinement_2d is True


def test_time_refinement_validation_generates_expected_summary(tmp_path: Path) -> None:
    result = run_time_refinement_validation_2d(base_output_dir=str(tmp_path / "benchmarks"))
    summary_path = Path(result["summary_path"])

    assert summary_path.exists()
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["study_name"] == "time_refinement_2d"
    assert "dt_levels" in payload
    assert len(payload["dt_levels"]) == 3
    assert "comparisons" in payload
    assert len(payload["comparisons"]) == 2
    assert payload["scientific_acceptance"] == "human_review_required"
    assert payload["summary"]["unexpected_failures"] == []
    assert payload["summary"]["runtime_execution"] == "passed"
    assert payload["summary"]["time_refinement_status"] in {"passed", "warning"}
