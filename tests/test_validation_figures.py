from __future__ import annotations

import json
from pathlib import Path

import pytest

from navier_stokes_research.cli import build_parser
from navier_stokes_research.validation_figures import generate_validation_figures
from navier_stokes_research.validation_schema import build_validation_result


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_cli_parser_supports_validation_figures_flag() -> None:
    parser = build_parser()
    args = parser.parse_args(["--validation-figures"])
    assert args.validation_figures is True


def test_generate_validation_figures_manifest_and_png(tmp_path: Path) -> None:
    base = tmp_path / "benchmarks"
    reports = tmp_path / "reports"
    figures = tmp_path / "figures"

    _write_json(
        base / "taylor_green_2d" / "taylor_green_validation.json",
        {
            "errors": {"l2": 1e-6, "linf": 2e-6, "relative": 3e-6},
            "execution_status": "passed",
            "accuracy_status": "passed",
        },
    )
    _write_json(
        base / "physical_decay_2d" / "physical_decay_validation.json",
        {
            "metrics_summary": {
                "initial_energy": 1.0,
                "final_energy": 0.9,
                "initial_enstrophy": 1.1,
                "final_enstrophy": 0.8,
            },
            "acceptance_statuses": {"runtime_execution": "passed", "physical_decay_status": "passed"},
        },
    )
    _write_json(
        base / "time_refinement_2d" / "time_refinement_summary.json",
        {
            "dt_levels": [
                {"dt": 0.01, "final_energy": 0.9},
                {"dt": 0.005, "final_energy": 0.89},
            ],
            "summary": {"runtime_execution": "passed", "time_refinement_status": "passed", "unexpected_failures": []},
        },
    )
    _write_json(
        base / "multi_resolution_energy_enstrophy_2d" / "multi_resolution_energy_enstrophy_summary.json",
        {
            **build_validation_result(
                validation_id="multi_resolution_energy_enstrophy_2d",
                validation_type="diagnostic",
                status="passed",
                claim_scope="numerical_regression_check",
            ),
            "resolutions": [
                {"resolution": 32, "energy_ratio": 0.99},
                {"resolution": 64, "energy_ratio": 0.98},
            ],
            "acceptance_statuses": {"runtime_execution": "passed", "energy_enstrophy_regression_status": "passed"},
            "summary": {"unexpected_failures": []},
        },
    )
    _write_json(base / "stress_validation_2d" / "stress_validation_summary.json", {"scenarios": []})
    _write_json(reports / "scientific_validation_report.json", {"ok": True})

    manifest = generate_validation_figures(
        base_benchmark_dir=str(base),
        report_path=str(reports / "scientific_validation_report.json"),
        output_dir=str(figures),
    )
    manifest_path = figures / "figures_manifest.json"
    assert manifest_path.exists()
    assert manifest["scientific_acceptance"] == "human_review_required"
    assert manifest["claim_policy"]["no_3d_claim"] is True
    assert manifest["claim_policy"]["no_millennium_claim"] is True
    assert manifest["claim_policy"]["no_formal_proof_claim"] is True
    assert manifest["summary"]["generated"] >= 1
    assert any(Path(item["path"]).exists() for item in manifest["figures"] if item["status"] == "generated")


def test_generate_validation_figures_marks_skipped_for_missing_data(tmp_path: Path) -> None:
    base = tmp_path / "benchmarks"
    reports = tmp_path / "reports"
    figures = tmp_path / "figures"
    _write_json(
        base / "multi_resolution_energy_enstrophy_2d" / "multi_resolution_energy_enstrophy_summary.json",
        {**build_validation_result(validation_id="a", validation_type="diagnostic", status="passed", claim_scope="diagnostic_only"), "resolutions": []},
    )
    _write_json(reports / "scientific_validation_report.json", {"ok": True})
    manifest = generate_validation_figures(
        base_benchmark_dir=str(base),
        report_path=str(reports / "scientific_validation_report.json"),
        output_dir=str(figures),
    )
    assert manifest["summary"]["skipped"] >= 1


def test_generate_validation_figures_fail_closed_on_corrupt_report_json(tmp_path: Path) -> None:
    base = tmp_path / "benchmarks"
    reports = tmp_path / "reports"
    figures = tmp_path / "figures"
    (reports / "scientific_validation_report.json").parent.mkdir(parents=True, exist_ok=True)
    (reports / "scientific_validation_report.json").write_text("{", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        generate_validation_figures(
            base_benchmark_dir=str(base),
            report_path=str(reports / "scientific_validation_report.json"),
            output_dir=str(figures),
        )
