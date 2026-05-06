from __future__ import annotations

import argparse
import json

from navier_stokes_research.hpc_benchmark import run_hpc_fftw_benchmark


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run baseline-vs-FFTW 2D periodic infrastructure benchmark."
    )
    parser.add_argument(
        "--base-output-dir",
        default="outputs/benchmarks",
        help="Base directory for benchmark artifacts.",
    )
    parser.add_argument(
        "--extended",
        action="store_true",
        help="Extended benchmark mode with more steps.",
    )
    args = parser.parse_args()
    result = run_hpc_fftw_benchmark(
        base_output_dir=args.base_output_dir,
        extended=args.extended,
    )
    payload = json.loads(result["summary_path"].read_text(encoding="utf-8"))
    if payload.get("execution_status") == "failed" or payload.get("benchmark_status") == "failed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
