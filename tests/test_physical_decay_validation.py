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
    spectral_diagnostics = Path(result["spectral_diagnostics_path"])
    final_snapshot = Path(result["final_snapshot_path"])

    assert json_path.exists()
    assert metrics_csv.exists()
    assert validation_report.exists()
    assert spectral_diagnostics.exists()
    assert final_snapshot.exists()
    assert final_snapshot.name == "vorticity_00160.npy"

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["study_name"] == "physical_decay_2d"
    assert payload["acceptance_statuses"]["runtime_execution"] in {"passed", "warning", "failed"}
    assert payload["acceptance_statuses"]["physical_decay_status"] in {"passed", "warning", "failed"}
    assert payload["acceptance_statuses"]["scientific_acceptance"] == "human_review_required"
    assert payload["spectral_evidence"]["status"] == "available"
    assert payload["spectral_evidence"]["interpretation"] == "diagnostic_only_not_hard_gate"
    assert payload["spectral_evidence"]["total_spectral_energy"] > 0.0
    assert 0.0 <= payload["spectral_evidence"]["high_wavenumber_energy_fraction"] <= 1.0
    assert payload["artifacts"]["spectral_diagnostics_json"] == str(spectral_diagnostics)


def test_physical_decay_validation_writes_spectral_diagnostics_json(tmp_path: Path) -> None:
    result = run_physical_decay_validation(base_output_dir=str(tmp_path / "benchmarks"))
    spectral_payload = json.loads(
        Path(result["spectral_diagnostics_path"]).read_text(encoding="utf-8")
    )

    assert spectral_payload["total_spectral_energy"] > 0.0
    assert spectral_payload["radial_wavenumbers"]
    assert spectral_payload["radial_energy"]
    assert 0.0 <= spectral_payload["high_wavenumber_energy_fraction"] <= 1.0
    assert spectral_payload["grid"] == {"nx": 64, "ny": 64}
    assert spectral_payload["domain"]["lx"] > 0.0
    assert spectral_payload["domain"]["ly"] > 0.0


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
    assert payload["spectral_evidence"]["status"] == "available"
