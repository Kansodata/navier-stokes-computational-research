from __future__ import annotations

import json
import inspect
from pathlib import Path

import matplotlib.pyplot as plt

from navier_stokes_research.cli import build_parser
import navier_stokes_research.scientific_report as scientific_report_module
from navier_stokes_research.scientific_report import (
    ArtifactSpec,
    PDF_FIGSIZE,
    _humanize_discrepancy,
    _select_generated_figure_paths,
    _short_path_label,
    _short_validation_name,
    _snake_case_to_sentence,
    generate_scientific_validation_pdf,
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


def test_cli_parser_supports_pdf_flag() -> None:
    parser = build_parser()
    args = parser.parse_args(["--scientific-validation-report", "--pdf"])
    assert args.scientific_validation_report is True
    assert args.pdf is True


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


def test_scientific_report_adds_discrepancy_analysis_for_warning_artifact(tmp_path: Path) -> None:
    base = tmp_path / "benchmarks"
    out = tmp_path / "reports"
    artifact = build_validation_result(
        validation_id="forced_turbulence_validation_2d",
        validation_type="diagnostic",
        status="warning",
        claim_scope="diagnostic_only",
        metrics={"accuracy_status": "warning"},
        notes=["diagnostic_only"],
    )
    artifact["summary"] = {"warnings": ["insufficient_inertial_range_for_slope_fit"]}
    artifact_path = (
        base
        / "forced_turbulence_validation_2d"
        / "forced_turbulence_validation_summary.json"
    )
    _write_json(artifact_path, artifact)

    result = generate_scientific_validation_report(
        base_benchmark_dir=str(base),
        output_dir=str(out),
        artifact_specs=[
            ArtifactSpec(
                validation_id="forced_turbulence_validation_2d",
                validation_type="diagnostic",
                path=artifact_path,
                critical=True,
            )
        ],
    )

    payload = json.loads(Path(result["report_json_path"]).read_text(encoding="utf-8"))
    assert payload["overall_status"] == "warning"
    assert payload["discrepancy_analysis"]
    analysis = payload["discrepancy_analysis"][0]
    assert analysis["external_reference"] == "kraichnan_leith_batchelor_reference_slopes_diagnostic_only"
    assert "insufficient_inertial_range_for_slope_fit" in analysis["warning_tokens"]
    assert "does_not_establish_formal_convergence_or_general_turbulence_validity" == analysis["claim_boundary"]

    markdown = Path(result["report_markdown_path"]).read_text(encoding="utf-8")
    assert "## Discrepancy Analysis" in markdown


def test_scientific_report_pdf_is_generated(tmp_path: Path) -> None:
    base = tmp_path / "benchmarks"
    out = tmp_path / "reports"
    artifact = build_validation_result(
        validation_id="unit_pdf_case",
        validation_type="diagnostic",
        status="passed",
        claim_scope="diagnostic_only",
        metrics={"x": 1.0},
    )
    artifact_path = base / "unit" / "artifact.json"
    _write_json(artifact_path, artifact)
    report = generate_scientific_validation_report(
        base_benchmark_dir=str(base),
        output_dir=str(out),
        artifact_specs=[
            ArtifactSpec(
                validation_id="unit_pdf_case",
                validation_type="diagnostic",
                path=artifact_path,
                critical=True,
            )
        ],
    )
    pdf_path = out / "scientific_validation_report.pdf"
    generated = generate_scientific_validation_pdf(
        report_json_path=str(report["report_json_path"]),
        output_pdf_path=str(pdf_path),
    )
    assert generated.exists()
    assert generated.suffix == ".pdf"
    assert generated.stat().st_size > 0


def test_scientific_report_pdf_fail_closed_when_critical_evidence_missing(tmp_path: Path) -> None:
    base = tmp_path / "benchmarks"
    out = tmp_path / "reports"
    missing_path = base / "missing" / "artifact.json"
    report = generate_scientific_validation_report(
        base_benchmark_dir=str(base),
        output_dir=str(out),
        artifact_specs=[
            ArtifactSpec(
                validation_id="critical_missing",
                validation_type="verification",
                path=missing_path,
                critical=True,
            )
        ],
    )
    pdf_path = out / "scientific_validation_report.pdf"
    try:
        generate_scientific_validation_pdf(
            report_json_path=str(report["report_json_path"]),
            output_pdf_path=str(pdf_path),
            fail_closed_on_failed=True,
        )
    except RuntimeError as exc:
        assert "Fail-closed" in str(exc)
    else:
        raise AssertionError("Expected fail-closed RuntimeError for failed overall status.")
    assert not pdf_path.exists()


def test_scientific_report_discrepancy_text_is_human_readable_not_raw_json() -> None:
    lines = _humanize_discrepancy(
        {
            "validation_id": "forced_turbulence_validation_2d",
            "warning_tokens": ["insufficient_inertial_range_for_slope_fit"],
            "likely_causes": ["warning_status_requires_human_review"],
            "recommended_actions": ["inspect_artifact_metrics_before_using_results"],
        }
    )
    joined = " ".join(lines)
    assert "{" not in joined
    assert "}" not in joined
    assert "json" not in joined.lower()


def test_short_helpers_produce_legible_labels() -> None:
    assert _short_validation_name("multi_resolution_energy_enstrophy_2d") == "Multi-Res E/E 2D"
    path = "C:/repo/outputs/benchmarks/taylor_green_2d/taylor_green_validation.json"
    assert _short_path_label(path).startswith("outputs/")


def test_pdf_generator_source_avoids_console_table_string() -> None:
    source = inspect.getsource(generate_scientific_validation_pdf)
    assert "validation_id | type | status | schema | path" not in source


def test_pdf_layout_constant_is_a4_portrait_and_no_landscape_pages() -> None:
    assert PDF_FIGSIZE == (8.27, 11.69)
    source = inspect.getsource(scientific_report_module)
    assert "figsize=(11.69, 8.27)" not in source


def test_snake_case_humanization_is_readable() -> None:
    assert _snake_case_to_sentence("warning_status_requires_human_review") == "Warning status requires human review"


def test_select_generated_figure_paths_reads_manifest(tmp_path: Path) -> None:
    figures_dir = tmp_path / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    image_path = figures_dir / "figure_1.png"
    fig, ax = plt.subplots(figsize=(2, 2))
    ax.plot([0, 1], [0, 1])
    fig.savefig(image_path)
    plt.close(fig)

    manifest_path = figures_dir / "figures_manifest.json"
    manifest = {
        "figures": [
            {"figure_id": "f1", "status": "generated", "path": str(image_path)},
            {"figure_id": "f2", "status": "skipped", "path": str(figures_dir / "missing.png")},
        ]
    }
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    selected = _select_generated_figure_paths(str(manifest_path))
    assert selected
    assert selected[0] == image_path


def test_scientific_report_pdf_with_generated_figures_manifest(tmp_path: Path) -> None:
    base = tmp_path / "benchmarks"
    out = tmp_path / "reports"
    figures_dir = tmp_path / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    artifact = build_validation_result(
        validation_id="unit_pdf_fig_case",
        validation_type="diagnostic",
        status="passed",
        claim_scope="diagnostic_only",
    )
    artifact_path = base / "unit" / "artifact.json"
    _write_json(artifact_path, artifact)
    image_path = figures_dir / "figure_1.png"
    fig, ax = plt.subplots(figsize=(2, 2))
    ax.plot([0, 1], [1, 0])
    fig.savefig(image_path)
    plt.close(fig)
    manifest = {
        "figures": [
            {"figure_id": "f1", "status": "generated", "path": str(image_path)},
        ]
    }
    manifest_path = figures_dir / "figures_manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    report = generate_scientific_validation_report(
        base_benchmark_dir=str(base),
        output_dir=str(out),
        figures_manifest_path=str(manifest_path),
        artifact_specs=[
            ArtifactSpec(
                validation_id="unit_pdf_fig_case",
                validation_type="diagnostic",
                path=artifact_path,
                critical=True,
            )
        ],
    )
    pdf_path = out / "scientific_validation_report.pdf"
    generated = generate_scientific_validation_pdf(
        report_json_path=str(report["report_json_path"]),
        output_pdf_path=str(pdf_path),
    )
    assert generated.exists()
    assert generated.stat().st_size > 0
