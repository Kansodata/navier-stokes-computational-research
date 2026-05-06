from __future__ import annotations

import json
from pathlib import Path

from navier_stokes_research.cli import build_parser
from navier_stokes_research.scientific_report import (
    ArtifactSpec,
    generate_scientific_validation_report,
)
from navier_stokes_research.validation_schema import build_validation_result


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_cli_parser_supports_scientific_validation_report_flag() -> None:
    parser = build_parser()
    args = parser.parse_args(["--scientific-validation-report"])
    assert args.scientific_validation_report is True


def test_scientific_report_generates_json_and_markdown(tmp_path: Path) -> None:
    base = tmp_path / "benchmarks"
    out = tmp_path / "reports"
    artifact = build_validation_result(
        validation_id="unit_validation",
        validation_type="diagnostic",
        status="passed",
        claim_scope="diagnostic_only",
        metrics={"x": 1.0},
    )
    artifact_path = base / "unit" / "artifact.json"
    _write_json(artifact_path, artifact)

    result = generate_scientific_validation_report(
        base_benchmark_dir=str(base),
        output_dir=str(out),
        artifact_specs=[
            ArtifactSpec(
                validation_id="unit_validation",
                validation_type="diagnostic",
                path=artifact_path,
                critical=True,
            )
        ],
    )

    report_json = Path(result["report_json_path"])
    report_md = Path(result["report_markdown_path"])
    assert report_json.exists()
    assert report_md.exists()

    payload = json.loads(report_json.read_text(encoding="utf-8"))
    for field in (
        "schema_version",
        "report_id",
        "generated_at_utc",
        "project_scope",
        "overall_status",
        "scientific_acceptance",
        "claim_policy",
        "summary",
        "sections",
    ):
        assert field in payload
    assert payload["scientific_acceptance"] == "human_review_required"
    assert payload["claim_policy"]["no_3d_claim"] is True
    assert payload["claim_policy"]["no_millennium_claim"] is True
    assert payload["claim_policy"]["no_formal_proof_claim"] is True
    assert payload["claim_policy"]["no_general_navier_stokes_solution_claim"] is True

    markdown = report_md.read_text(encoding="utf-8")
    assert "## Scientific Limitations" in markdown
    assert "Not a 3D result." in markdown
    assert "Not a Millennium Problem solution." in markdown


def test_scientific_report_failed_status_makes_overall_failed(tmp_path: Path) -> None:
    base = tmp_path / "benchmarks"
    out = tmp_path / "reports"
    artifact = build_validation_result(
        validation_id="failed_case",
        validation_type="validation",
        status="failed",
        claim_scope="physical_consistency_validation_2d",
    )
    artifact_path = base / "unit" / "failed.json"
    _write_json(artifact_path, artifact)

    result = generate_scientific_validation_report(
        base_benchmark_dir=str(base),
        output_dir=str(out),
        artifact_specs=[
            ArtifactSpec(
                validation_id="failed_case",
                validation_type="validation",
                path=artifact_path,
                critical=True,
            )
        ],
    )
    assert result["overall_status"] == "failed"


def test_scientific_report_unknown_status_is_fail_closed(tmp_path: Path) -> None:
    base = tmp_path / "benchmarks"
    out = tmp_path / "reports"
    payload = build_validation_result(
        validation_id="unknown_status_case",
        validation_type="diagnostic",
        status="passed",
        claim_scope="diagnostic_only",
    )
    payload["status"] = "unknown_status"
    artifact_path = base / "unit" / "unknown.json"
    _write_json(artifact_path, payload)

    result = generate_scientific_validation_report(
        base_benchmark_dir=str(base),
        output_dir=str(out),
        artifact_specs=[
            ArtifactSpec(
                validation_id="unknown_status_case",
                validation_type="diagnostic",
                path=artifact_path,
                critical=True,
            )
        ],
    )
    assert result["overall_status"] == "failed"


def test_scientific_report_missing_artifact_is_listed(tmp_path: Path) -> None:
    out = tmp_path / "reports"
    missing_path = tmp_path / "benchmarks" / "missing" / "artifact.json"
    result = generate_scientific_validation_report(
        base_benchmark_dir=str(tmp_path / "benchmarks"),
        output_dir=str(out),
        artifact_specs=[
            ArtifactSpec(
                validation_id="missing_case",
                validation_type="verification",
                path=missing_path,
                critical=True,
            )
        ],
    )
    payload = json.loads(Path(result["report_json_path"]).read_text(encoding="utf-8"))
    assert "missing_case" in payload["missing_artifacts"]


def test_scientific_report_legacy_artifact_is_classified(tmp_path: Path) -> None:
    base = tmp_path / "benchmarks"
    out = tmp_path / "reports"
    legacy_payload = {
        "study_name": "time_refinement_2d",
        "summary": {"runtime_execution": "passed", "time_refinement_status": "warning"},
    }
    artifact_path = base / "time_refinement_2d" / "time_refinement_summary.json"
    _write_json(artifact_path, legacy_payload)

    result = generate_scientific_validation_report(
        base_benchmark_dir=str(base),
        output_dir=str(out),
        artifact_specs=[
            ArtifactSpec(
                validation_id="time_refinement_2d",
                validation_type="diagnostic",
                path=artifact_path,
                critical=True,
            )
        ],
    )
    payload = json.loads(Path(result["report_json_path"]).read_text(encoding="utf-8"))
    assert "time_refinement_2d" in payload["legacy_artifacts"]
