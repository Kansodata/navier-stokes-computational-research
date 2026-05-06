from __future__ import annotations

import argparse

from navier_stokes_research.resolution_sensitivity_study import (
    DEFAULT_FINAL_TIME,
    EXTENDED_RESOLUTIONS,
    run_resolution_sensitivity_study_2d,
)


def _parse_resolutions(value: str) -> tuple[int, ...]:
    return tuple(int(item.strip()) for item in value.split(",") if item.strip())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the forced 2D resolution sensitivity diagnostic study."
    )
    parser.add_argument(
        "--base-output-dir",
        default="outputs/benchmarks",
        help="Base directory for benchmark artifacts.",
    )
    parser.add_argument(
        "--resolutions",
        default=",".join(str(item) for item in EXTENDED_RESOLUTIONS),
        help="Comma-separated resolution list. Default: 64,128,256,512.",
    )
    parser.add_argument(
        "--final-time",
        type=float,
        default=DEFAULT_FINAL_TIME,
        help="Short diagnostic physical horizon used by every resolution.",
    )
    args = parser.parse_args()
    run_resolution_sensitivity_study_2d(
        base_output_dir=args.base_output_dir,
        resolutions=_parse_resolutions(args.resolutions),
        final_time=args.final_time,
    )


if __name__ == "__main__":
    main()
