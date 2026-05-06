from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from navier_stokes_research.validation_schema import CANONICAL_SOLVER_SCOPE

FORBIDDEN_CLAIM_TOKENS = ("3d", "millennium", "proof", "formal_resolution")


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be object: {path}")
    return payload


def _ensure_safe_claim_scope(payload: dict[str, Any], context: str) -> None:
    claim_scope = payload.get("claim_scope")
    if not isinstance(claim_scope, str):
        return
    lowered = claim_scope.lower()
    for token in FORBIDDEN_CLAIM_TOKENS:
        if token in lowered:
            raise ValueError(f"Unsafe claim_scope token '{token}' in {context}")


def _write_figure(
    path: Path,
    title: str,
    x: list[float],
    y: list[float],
    ylabel: str,
    tick_labels: list[str] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 4), dpi=120)
    ax.plot(x, y, marker="o")
    if tick_labels is not None:
        ax.set_xticks(x)
        ax.set_xticklabels(tick_labels, rotation=25, ha="right")
    ax.set_title(title)
    ax.set_xlabel("Index")
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.35)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def generate_validation_figures(
    *,
    base_benchmark_dir: str = "outputs/benchmarks",
    report_path: str = "outputs/reports/scientific_validation_report.json",
    output_dir: str = "outputs/figures",
) -> dict[str, Any]:
    benchmark_root = Path(base_benchmark_dir)
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    figures: list[dict[str, Any]] = []

    def add_figure(
        figure_id: str,
        title: str,
        file_name: str,
        validation_type: str,
        source_artifacts: list[str],
        generator: Any,
        limitations: list[str],
    ) -> None:
        figure_path = output_root / file_name
        try:
            generated = generator(figure_path)
            if not generated:
                figures.append(
                    {
                        "figure_id": figure_id,
                        "title": title,
                        "path": str(figure_path),
                        "source_artifacts": source_artifacts,
                        "status": "skipped",
                        "validation_type": validation_type,
                        "limitations": limitations + ["insufficient_data"],
                    }
                )
                return
            figures.append(
                {
                    "figure_id": figure_id,
                    "title": title,
                    "path": str(figure_path),
                    "source_artifacts": source_artifacts,
                    "status": "generated",
                    "validation_type": validation_type,
                    "limitations": limitations,
                }
            )
        except FileNotFoundError:
            figures.append(
                {
                    "figure_id": figure_id,
                    "title": title,
                    "path": str(figure_path),
                    "source_artifacts": source_artifacts,
                    "status": "skipped",
                    "validation_type": validation_type,
                    "limitations": limitations + ["missing_artifact"],
                }
            )
        except Exception as exc:  # noqa: BLE001
            figures.append(
                {
                    "figure_id": figure_id,
                    "title": title,
                    "path": str(figure_path),
                    "source_artifacts": source_artifacts,
                    "status": "failed",
                    "validation_type": validation_type,
                    "limitations": limitations + [f"unexpected_error:{type(exc).__name__}"],
                }
            )

    def taylor_green(path: Path) -> bool:
        source = benchmark_root / "taylor_green_2d" / "taylor_green_validation.json"
        payload = _load_json(source)
        errors = payload.get("errors")
        if not isinstance(errors, dict):
            return False
        x = []
        y = []
        for key in ("l2", "linf", "relative"):
            value = errors.get(key)
            if isinstance(value, (int, float)):
                x.append(key)
                y.append(float(value))
        if not y:
            return False
        _write_figure(
            path,
            "Taylor-Green 2D Error Metrics (Controlled)",
            [float(i) for i in range(len(x))],
            y,
            "Error",
            tick_labels=x,
        )
        return True

    def physical_decay(path: Path) -> bool:
        source = benchmark_root / "physical_decay_2d" / "physical_decay_validation.json"
        payload = _load_json(source)
        metrics = payload.get("metrics_summary")
        if not isinstance(metrics, dict):
            return False
        data = []
        labels = []
        for key in (
            "initial_energy",
            "final_energy",
            "initial_enstrophy",
            "final_enstrophy",
        ):
            value = metrics.get(key)
            if isinstance(value, (int, float)):
                labels.append(key)
                data.append(float(value))
        if len(data) < 2:
            return False
        _write_figure(
            path,
            "Physical Decay 2D Energy/Enstrophy Summary",
            [float(i) for i in range(len(labels))],
            data,
            "Value",
            tick_labels=labels,
        )
        return True

    def time_refinement(path: Path) -> bool:
        source = benchmark_root / "time_refinement_2d" / "time_refinement_summary.json"
        payload = _load_json(source)
        dt_levels = payload.get("dt_levels")
        if not isinstance(dt_levels, list) or not dt_levels:
            return False
        dt = []
        energy = []
        for item in dt_levels:
            if not isinstance(item, dict):
                continue
            dt_value = item.get("dt")
            energy_value = item.get("final_energy")
            if isinstance(dt_value, (int, float)) and isinstance(energy_value, (int, float)):
                dt.append(float(dt_value))
                energy.append(float(energy_value))
        if len(energy) < 2:
            return False
        _write_figure(
            path,
            "Time Refinement 2D Final Energy by dt (Diagnostic)",
            [float(i) for i in range(len(dt))],
            energy,
            "Final energy",
            tick_labels=[f"{value:.5f}" for value in dt],
        )
        return True

    def multi_resolution(path: Path) -> bool:
        source = (
            benchmark_root
            / "multi_resolution_energy_enstrophy_2d"
            / "multi_resolution_energy_enstrophy_summary.json"
        )
        payload = _load_json(source)
        _ensure_safe_claim_scope(payload, "multi_resolution_energy_enstrophy_2d")
        rows = payload.get("resolutions")
        if not isinstance(rows, list) or not rows:
            return False
        resolution = []
        ratios = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            n = row.get("resolution")
            ratio = row.get("energy_ratio")
            if isinstance(n, int) and isinstance(ratio, (int, float)):
                resolution.append(str(n))
                ratios.append(float(ratio))
        if not ratios:
            return False
        _write_figure(
            path,
            "Multi-resolution 2D Energy Ratio (Diagnostic Regression)",
            [float(i) for i in range(len(resolution))],
            ratios,
            "Energy ratio",
            tick_labels=resolution,
        )
        return True

    def stress_validation(path: Path) -> bool:
        source = benchmark_root / "stress_validation_2d" / "stress_validation_summary.json"
        payload = _load_json(source)
        scenarios = payload.get("scenarios")
        if not isinstance(scenarios, list) or not scenarios:
            return False
        labels: list[str] = []
        values: list[float] = []
        for scenario in scenarios:
            if not isinstance(scenario, dict):
                continue
            name = scenario.get("name")
            summary = scenario.get("metrics_summary")
            if not isinstance(summary, dict):
                continue
            cfl_peak = summary.get("cfl_peak")
            if isinstance(name, str) and isinstance(cfl_peak, (int, float)):
                labels.append(name)
                values.append(float(cfl_peak))
        if not values:
            return False
        _write_figure(
            path,
            "Stress Validation 2D CFL Peak (Diagnostic)",
            [float(i) for i in range(len(labels))],
            values,
            "CFL peak",
            tick_labels=labels,
        )
        return True

    add_figure(
        "taylor_green_2d_error",
        "Taylor-Green 2D controlled error metrics",
        "taylor_green_2d_error.png",
        "verification",
        [str(benchmark_root / "taylor_green_2d" / "taylor_green_validation.json")],
        taylor_green,
        ["controlled_2d_case_only", "not_a_formal_proof"],
    )
    add_figure(
        "physical_decay_2d_energy_enstrophy",
        "Physical decay 2D energy/enstrophy summary",
        "physical_decay_2d_energy_enstrophy.png",
        "validation",
        [str(benchmark_root / "physical_decay_2d" / "physical_decay_validation.json")],
        physical_decay,
        ["2d_periodic_scope_only", "not_universal_physical_validation"],
    )
    add_figure(
        "time_refinement_2d_summary",
        "Time refinement 2D summary",
        "time_refinement_2d_summary.png",
        "diagnostic",
        [str(benchmark_root / "time_refinement_2d" / "time_refinement_summary.json")],
        time_refinement,
        ["diagnostic_only_not_formal_convergence_proof"],
    )
    add_figure(
        "multi_resolution_energy_enstrophy_2d_summary",
        "Multi-resolution energy/enstrophy 2D summary",
        "multi_resolution_energy_enstrophy_2d_summary.png",
        "diagnostic",
        [
            str(
                benchmark_root
                / "multi_resolution_energy_enstrophy_2d"
                / "multi_resolution_energy_enstrophy_summary.json"
            )
        ],
        multi_resolution,
        ["diagnostic_regression_only_not_formal_convergence_proof"],
    )
    add_figure(
        "stress_validation_2d_summary",
        "Stress validation 2D summary",
        "stress_validation_2d_summary.png",
        "diagnostic",
        [str(benchmark_root / "stress_validation_2d" / "stress_validation_summary.json")],
        stress_validation,
        ["stress_diagnostic_only"],
    )

    if Path(report_path).exists():
        _load_json(Path(report_path))

    summary = {
        "generated": sum(1 for figure in figures if figure["status"] == "generated"),
        "skipped": sum(1 for figure in figures if figure["status"] == "skipped"),
        "failed": sum(1 for figure in figures if figure["status"] == "failed"),
    }
    manifest = {
        "schema_version": "1.0",
        "generated_at_utc": _utc_now(),
        "project_scope": CANONICAL_SOLVER_SCOPE,
        "scientific_acceptance": "human_review_required",
        "figures": figures,
        "summary": summary,
        "claim_policy": {
            "no_3d_claim": True,
            "no_millennium_claim": True,
            "no_formal_proof_claim": True,
        },
    }
    manifest_path = output_root / "figures_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest
