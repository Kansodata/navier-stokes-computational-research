from __future__ import annotations

from pathlib import Path

import pytest

from navier_stokes_research.visualization import save_taylor_green_error_diagnostics


def test_save_taylor_green_error_diagnostics_creates_expected_files(tmp_path: Path) -> None:
    rows = [
        {"resolution": 32, "l2_error": 1e-2, "linf_error": 2e-2, "relative_error": 3e-2},
        {"resolution": 64, "l2_error": 5e-3, "linf_error": 1e-2, "relative_error": 1.5e-2},
        {"resolution": 128, "l2_error": 2.5e-3, "linf_error": 5e-3, "relative_error": 7.5e-3},
    ]
    artifacts = save_taylor_green_error_diagnostics(
        rows=rows,
        output_dir=tmp_path / "plots",
        roundoff_floor=1e-12,
    )
    expected = {
        "taylor_green_l2_error_by_resolution.png",
        "taylor_green_linf_error_by_resolution.png",
        "taylor_green_relative_l2_error_by_resolution.png",
        "taylor_green_combined_error_logscale.png",
    }
    assert expected.issubset(set(artifacts.keys()))
    for artifact in expected:
        assert Path(artifacts[artifact]).exists()


def test_save_taylor_green_error_diagnostics_rejects_invalid_roundoff_floor(tmp_path: Path) -> None:
    rows = [{"resolution": 32, "l2_error": 1e-2, "linf_error": 2e-2, "relative_error": 3e-2}]
    with pytest.raises(ValueError):
        save_taylor_green_error_diagnostics(
            rows=rows,
            output_dir=tmp_path / "plots",
            roundoff_floor=0.0,
        )
