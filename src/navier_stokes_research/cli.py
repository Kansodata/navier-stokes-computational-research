from __future__ import annotations

import argparse
import json
from dataclasses import replace

from navier_stokes_research.benchmark import run_benchmark
from navier_stokes_research.config import load_config
from navier_stokes_research.convergence import run_convergence_study
from navier_stokes_research.external_validation import run_external_reference_validation_2d
from navier_stokes_research.forcing_validator import run_forced_turbulence_validation_2d
from navier_stokes_research.logging_utils import configure_logging
from navier_stokes_research.multi_resolution_validation import (
    run_multi_resolution_energy_enstrophy_validation_2d,
)
from navier_stokes_research.physical_decay import run_physical_decay_validation
from navier_stokes_research.runner import run_simulation
from navier_stokes_research.resolution_sensitivity_study import (
    DEFAULT_RESOLUTIONS,
    EXTENDED_RESOLUTIONS,
    run_resolution_sensitivity_study_2d,
)
from navier_stokes_research.scientific_report import generate_scientific_validation_report
from navier_stokes_research.stress_validation import run_stress_validation_2d
from navier_stokes_research.time_refinement import run_time_refinement_validation_2d
from navier_stokes_research.taylor_green import run_taylor_green_convergence_study, run_taylor_green_validation
from navier_stokes_research.validation_figures import generate_validation_figures


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run 2D incompressible Navier-Stokes experiments."
    )
    parser.add_argument(
        "--config",
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
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run post-simulation validation checks and write validation_report.json.",
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run the reproducible benchmark configuration.",
    )
    parser.add_argument(
        "--benchmark-output-dir",
        default="outputs/benchmarks",
        help="Base directory for benchmark artifacts.",
    )
    parser.add_argument(
        "--convergence-study",
        action="store_true",
        help="Run the reproducible convergence study harness.",
    )
    parser.add_argument(
        "--convergence-output-dir",
        default="outputs/convergence",
        help="Base directory for convergence-study artifacts.",
    )
    parser.add_argument(
        "--convergence-extended",
        action="store_true",
        help="Include the optional 128x128 resolution in the convergence study.",
    )
    parser.add_argument(
        "--taylor-green-validation",
        action="store_true",
        help="Run controlled 2D Taylor-Green validation and write taylor_green_validation.json.",
    )
    parser.add_argument(
        "--taylor-green-convergence",
        action="store_true",
        help="Run Taylor-Green validation across resolutions and estimate error convergence orders.",
    )
    parser.add_argument(
        "--physical-decay-validation",
        action="store_true",
        help="Run controlled 2D unforced viscous decay validation and write physical_decay_validation.json.",
    )
    parser.add_argument(
        "--stress-validation-2d",
        action="store_true",
        help="Run controlled 2D stress validation and write stress_validation_summary.json.",
    )
    parser.add_argument(
        "--external-validation-2d",
        action="store_true",
        help="Run external-reference validation harness and write external_reference_validation_summary.json.",
    )
    parser.add_argument(
        "--time-refinement-2d",
        action="store_true",
        help="Run 2D time-refinement validation harness and write time_refinement_summary.json.",
    )
    parser.add_argument(
        "--multi-resolution-energy-enstrophy-2d",
        action="store_true",
        help="Run 2D multi-resolution energy/enstrophy regression harness and write multi_resolution_energy_enstrophy_summary.json.",
    )
    parser.add_argument(
        "--scientific-validation-report",
        action="store_true",
        help="Generate consolidated scientific validation report JSON/Markdown from validation artifacts.",
    )
    parser.add_argument(
        "--validation-figures",
        action="store_true",
        help="Generate reproducible validation figures and figures_manifest.json.",
    )
    parser.add_argument(
        "--forced-turbulence-validation-2d",
        action="store_true",
        help="Run controlled 2D forced-turbulence diagnostics and write forced_turbulence_validation_summary.json.",
    )
    parser.add_argument(
        "--resolution-sensitivity-study-2d",
        action="store_true",
        help="Run controlled 2D forced-resolution sensitivity diagnostics and write resolution_sensitivity_summary.json.",
    )
    parser.add_argument(
        "--resolution-sensitivity-extended",
        action="store_true",
        help="Use the extended 64,128,256,512 matrix for --resolution-sensitivity-study-2d.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.benchmark:
        configure_logging("INFO")
        run_benchmark(base_output_dir=args.benchmark_output_dir)
        return

    if args.convergence_study:
        configure_logging("INFO")
        run_convergence_study(
            base_output_dir=args.convergence_output_dir,
            extended=args.convergence_extended,
        )
        return

    if args.taylor_green_validation:
        configure_logging("INFO")
        run_taylor_green_validation(base_output_dir=args.benchmark_output_dir)
        return

    if args.taylor_green_convergence:
        configure_logging("INFO")
        run_taylor_green_convergence_study(base_output_dir=args.benchmark_output_dir)
        return

    if args.physical_decay_validation:
        configure_logging("INFO")
        run_physical_decay_validation(base_output_dir=args.benchmark_output_dir)
        return

    if args.stress_validation_2d:
        configure_logging("INFO")
        run_stress_validation_2d(base_output_dir=args.benchmark_output_dir)
        return

    if args.external_validation_2d:
        configure_logging("INFO")
        run_external_reference_validation_2d(base_output_dir=args.benchmark_output_dir)
        return

    if args.time_refinement_2d:
        configure_logging("INFO")
        run_time_refinement_validation_2d(base_output_dir=args.benchmark_output_dir)
        return

    if args.multi_resolution_energy_enstrophy_2d:
        configure_logging("INFO")
        run_multi_resolution_energy_enstrophy_validation_2d(
            base_output_dir=args.benchmark_output_dir
        )
        return
    if args.scientific_validation_report:
        configure_logging("INFO")
        result = generate_scientific_validation_report(
            base_benchmark_dir=args.benchmark_output_dir
        )
        if result["overall_status"] == "failed":
            raise SystemExit(1)
        return
    if args.validation_figures:
        configure_logging("INFO")
        manifest = generate_validation_figures(
            base_benchmark_dir=args.benchmark_output_dir,
        )
        if manifest["summary"]["failed"] > 0:
            raise SystemExit(1)
        return
    if args.forced_turbulence_validation_2d:
        configure_logging("INFO")
        run_forced_turbulence_validation_2d(base_output_dir=args.benchmark_output_dir)
        return
    if args.resolution_sensitivity_study_2d:
        configure_logging("INFO")
        result = run_resolution_sensitivity_study_2d(
            base_output_dir=args.benchmark_output_dir,
            resolutions=EXTENDED_RESOLUTIONS if args.resolution_sensitivity_extended else DEFAULT_RESOLUTIONS,
        )
        if result["summary_path"].exists():
            # Warnings remain valid diagnostic output; explicit failed runs are not acceptable.
            payload = json.loads(result["summary_path"].read_text(encoding="utf-8"))
            if payload.get("status") == "failed":
                raise SystemExit(1)
        return

    if not args.config:
        raise ValueError(
            "--config is required unless --benchmark, --convergence-study, --taylor-green-validation, --taylor-green-convergence, --physical-decay-validation, --stress-validation-2d, --external-validation-2d, --time-refinement-2d, --multi-resolution-energy-enstrophy-2d, --scientific-validation-report, --validation-figures, --forced-turbulence-validation-2d, or --resolution-sensitivity-study-2d is used."
        )

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
    run_simulation(config, validate=args.validate)


if __name__ == "__main__":
    main()
