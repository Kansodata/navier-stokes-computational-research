from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from navier_stokes_research.cli import build_parser
from navier_stokes_research.mms_validation import run_mms_validation_2d


def test_mms_cli_flag_exists() -> None:
    parser = build_parser()
    args = parser.parse_args(["--mms-validation-2d"])
    assert args.mms_validation_2d is True


def test_mms_validation_writes_summary(tmp_path: Path) -> None:
    result = run_mms_validation_2d(base_output_dir=str(tmp_path / "benchmarks"))
    summary_path = Path(result["summary_path"])
    assert summary_path.exists()
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert payload["validation_name"] == "mms_validation_2d"
    assert payload["status"] in {"passed", "failed"}
    assert np.isfinite(payload["max_absolute_error"])
    assert np.isfinite(payload["l2_relative_error"])
