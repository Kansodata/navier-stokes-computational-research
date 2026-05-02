from __future__ import annotations

import argparse
from dataclasses import replace

from navier_stokes_research.config import load_config
from navier_stokes_research.logging_utils import configure_logging
from navier_stokes_research.runner import run_simulation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run 2D incompressible Navier-Stokes experiments."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to a JSON configuration file.",
    )
    parser.add_argument(
        "--output-dir",
        help="Override the configured output directory.",
    )
    parser.add_argument(
        "--steps",
        type=int,
        help="Override the number of time steps.",
    )
    parser.add_argument(
        "--dt",
        type=float,
        help="Override the time step.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(args.config)

    if args.output_dir or args.steps or args.dt:
        time_config = replace(
            config.time,
            steps=args.steps if args.steps is not None else config.time.steps,
            dt=args.dt if args.dt is not None else config.time.dt,
        )
        output_config = replace(
            config.output,
            output_dir=args.output_dir or config.output.output_dir,
        )
        config = replace(config, time=time_config, output=output_config)

    configure_logging(config.output.log_level)
    run_simulation(config)


if __name__ == "__main__":
    main()
