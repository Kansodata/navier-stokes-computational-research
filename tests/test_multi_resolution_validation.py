from __future__ import annotations

import json
from pathlib import Path

from navier_stokes_research.cli import build_parser
from navier_stokes_research.multi_resolution_validation import (
    SCENARIO_STATUSES,
    run_multi_resolution_energy_enstrophy_validation_2d,
)


def test_cli_parser_supports_multi_resolution_energy_enstrophy_flag() -> None:
    parser = build_parser()
    args = parser.parse_args(["--multi-resolution-energy-enstrophy-2d"])
    assert args.multi_resolution_energy_enstrophy_2d is True


def test_multi_resolution_energy_enstrophy_validation_summary_schema(tmp_path: Path) -> None:
    result = run_multi_resolution_energy_enstrophy_validation_2d(
        base_output_dir=str(tmp_path / "benchmarks")
    )
    summary_path = Path(result["summary_path"])
    assert summary_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    for required in (
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
        assert required in payload
    assert payload["schema_version"] == "1.0"
    assert payload["validation_type"] in {"verification", "validation", "diagnostic"}
    assert payload["status"] in {"passed", "warning", "failed", "skipped"}
    assert payload["solver_scope"] == "2d_incompressible_periodic_pseudo_spectral"
    forbidden_claim_terms = ("3d", "millennium", "proof", "formal_resolution")
    assert all(token not in payload["claim_scope"].lower() for token in forbidden_claim_terms)

    assert payload["study_name"] == "multi_resolution_energy_enstrophy_2d"
    assert payload["scientific_acceptance"] == "human_review_required"
    assert "resolutions" in payload and isinstance(payload["resolutions"], list)
    assert len(payload["resolutions"]) >= 3
    assert "summary" in payload and isinstance(payload["summary"], dict)
    assert payload["summary"]["unexpected_failures"] == []

    acceptance = payload["acceptance_statuses"]
    assert acceptance["runtime_execution"] in {"passed", "failed"}
    assert acceptance["energy_enstrophy_regression_status"] in {"passed", "warning", "failed"}

    for item in payload["resolutions"]:
        assert item["status"] in SCENARIO_STATUSES
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
            assert isinstance(item[key], (float, int))
