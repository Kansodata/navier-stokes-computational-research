from __future__ import annotations

import json
from pathlib import Path

from navier_stokes_research.cli import build_parser
from navier_stokes_research.external_validation import run_external_reference_validation_2d


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_cli_parser_supports_external_validation_2d_flag() -> None:
    parser = build_parser()
    args = parser.parse_args(["--external-validation-2d"])
    assert args.external_validation_2d is True


def test_external_reference_validation_generates_expected_summary(tmp_path: Path) -> None:
    base_output_dir = tmp_path / "benchmarks"
    _write_json(
        base_output_dir / "taylor_green_2d" / "taylor_green_validation.json",
        {
            "errors": {"l2": 1e-14, "linf": 2e-14, "relative": 3e-14},
            "status": "passed",
        },
    )
    _write_json(
        base_output_dir / "physical_decay_2d" / "physical_decay_validation.json",
        {
            "metrics_summary": {
                "initial_energy": 1.0,
                "final_energy": 0.95,
                "initial_enstrophy": 2.0,
                "final_enstrophy": 1.9,
            },
            "spectral_evidence": {
                "high_wavenumber_energy_fraction": 1e-8,
                "artifact": "outputs/benchmarks/physical_decay_2d/spectral_diagnostics.json",
            },
        },
    )
    _write_json(
        base_output_dir / "stress_validation_2d" / "stress_validation_summary.json",
        {"summary": {"non_expected_failures": []}},
    )

    result = run_external_reference_validation_2d(base_output_dir=str(base_output_dir))
    summary_path = Path(result["summary_path"])
    assert summary_path.exists()

    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["study_name"] == "external_reference_validation_2d"
    assert payload["overall_status"] == "passed"
    assert payload["checks"]["taylor_green_2d"]["status"] == "passed_roundoff_floor"
    assert payload["checks"]["energy_enstrophy_decay"]["status"] == "passed"
    assert payload["checks"]["spectral_consistency"]["status"] == "diagnostic_only"
    assert payload["checks"]["stress_validation"]["status"] == "passed"
    assert payload["checks"]["stress_validation"]["unexpected_failures"] == []


def test_external_reference_validation_fails_on_unexpected_stress_failures(tmp_path: Path) -> None:
    base_output_dir = tmp_path / "benchmarks"
    _write_json(
        base_output_dir / "taylor_green_2d" / "taylor_green_validation.json",
        {
            "errors": {"l2": 1e-14, "linf": 2e-14, "relative": 3e-14},
            "status": "passed",
        },
    )
    _write_json(
        base_output_dir / "physical_decay_2d" / "physical_decay_validation.json",
        {
            "metrics_summary": {
                "initial_energy": 1.0,
                "final_energy": 1.05,
                "initial_enstrophy": 2.0,
                "final_enstrophy": 2.05,
            },
            "spectral_evidence": {},
        },
    )
    _write_json(
        base_output_dir / "stress_validation_2d" / "stress_validation_summary.json",
        {"summary": {"non_expected_failures": ["near_cfl_limit"]}},
    )

    result = run_external_reference_validation_2d(base_output_dir=str(base_output_dir))
    payload = json.loads(Path(result["summary_path"]).read_text(encoding="utf-8"))
    assert payload["overall_status"] == "failed"
    assert payload["checks"]["stress_validation"]["status"] == "failed"
    assert payload["checks"]["stress_validation"]["unexpected_failures"] == ["near_cfl_limit"]
    assert "stress_validation_unexpected_failures" in payload["hard_failures"]
