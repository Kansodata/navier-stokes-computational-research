from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import textwrap
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from navier_stokes_research.validation_schema import (
    ALLOWED_STATUSES,
    ALLOWED_VALIDATION_TYPES,
    CANONICAL_SOLVER_SCOPE,
)

FORBIDDEN_CLAIM_TOKENS = ("3d", "millennium", "proof", "formal_resolution")


@dataclass(frozen=True)
class ArtifactSpec:
    validation_id: str
    validation_type: str
    path: Path
    critical: bool = True


def _default_artifact_specs(base_benchmark_dir: Path) -> list[ArtifactSpec]:
    return [
        ArtifactSpec(
            validation_id="taylor_green_2d",
            validation_type="verification",
            path=base_benchmark_dir / "taylor_green_2d" / "taylor_green_validation.json",
        ),
        ArtifactSpec(
            validation_id="taylor_green_convergence_2d",
            validation_type="verification",
            path=base_benchmark_dir
            / "taylor_green_convergence_2d"
            / "taylor_green_convergence_summary.json",
        ),
        ArtifactSpec(
            validation_id="physical_decay_2d",
            validation_type="validation",
            path=base_benchmark_dir / "physical_decay_2d" / "physical_decay_validation.json",
        ),
        ArtifactSpec(
            validation_id="stress_validation_2d",
            validation_type="diagnostic",
            path=base_benchmark_dir / "stress_validation_2d" / "stress_validation_summary.json",
        ),
        ArtifactSpec(
            validation_id="time_refinement_2d",
            validation_type="diagnostic",
            path=base_benchmark_dir / "time_refinement_2d" / "time_refinement_summary.json",
        ),
        ArtifactSpec(
            validation_id="multi_resolution_energy_enstrophy_2d",
            validation_type="diagnostic",
            path=base_benchmark_dir
            / "multi_resolution_energy_enstrophy_2d"
            / "multi_resolution_energy_enstrophy_summary.json",
        ),
        ArtifactSpec(
            validation_id="forced_turbulence_validation_2d",
            validation_type="diagnostic",
            path=base_benchmark_dir
            / "forced_turbulence_validation_2d"
            / "forced_turbulence_validation_summary.json",
        ),
        ArtifactSpec(
            validation_id="resolution_sensitivity_2d",
            validation_type="diagnostic",
            path=base_benchmark_dir
            / "resolution_sensitivity_2d"
            / "resolution_sensitivity_summary.json",
            critical=False,
        ),
        ArtifactSpec(
            validation_id="hpc_fftw_benchmark",
            validation_type="diagnostic",
            path=base_benchmark_dir
            / "hpc_fftw_benchmark"
            / "hpc_fftw_benchmark_summary.json",
            critical=False,
        ),
    ]


def _is_bad_status(value: str) -> bool:
    lowered = value.lower()
    return lowered in {"failed", "error", "invalid", "unknown"} or lowered.startswith("fail")


def _normalize_status_for_report(value: Any) -> str:
    if not isinstance(value, str):
        return "failed"
    lowered = value.lower()
    if _is_bad_status(lowered):
        return "failed"
    if lowered in {"warning", "warn", "human_review_required", "not_evaluated"}:
        return "warning"
    if lowered in {"skipped"}:
        return "skipped"
    if lowered in {"passed", "pass", "ok", "passed_roundoff_floor"}:
        return "passed"
    return "failed"


def _contains_forbidden_claim(text: str) -> bool:
    lowered = text.lower()
    return any(token in lowered for token in FORBIDDEN_CLAIM_TOKENS)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON root must be an object.")
    return payload


def _validate_schema_payload(payload: dict[str, Any]) -> list[str]:
    notes: list[str] = []
    required = (
        "schema_version",
        "validation_id",
        "validation_type",
        "status",
        "generated_at_utc",
        "solver_scope",
        "claim_scope",
        "parameters",
        "metrics",
        "thresholds",
        "artifacts",
        "limitations",
        "notes",
    )
    missing = [field for field in required if field not in payload]
    if missing:
        raise ValueError(f"Missing required schema fields: {missing}")
    if payload["schema_version"] != "1.0":
        raise ValueError("schema_version must be '1.0'.")
    if payload["validation_type"] not in ALLOWED_VALIDATION_TYPES:
        raise ValueError(f"Unknown validation_type: {payload['validation_type']}")
    if payload["status"] not in ALLOWED_STATUSES:
        raise ValueError(f"Unknown status: {payload['status']}")
    if payload["solver_scope"] != CANONICAL_SOLVER_SCOPE:
        raise ValueError("solver_scope mismatch.")
    claim_scope = payload["claim_scope"]
    if not isinstance(claim_scope, str):
        raise ValueError("claim_scope must be a string.")
    if _contains_forbidden_claim(claim_scope):
        raise ValueError(f"Unsafe claim_scope: {claim_scope}")
    for key in ("parameters", "metrics", "thresholds", "artifacts"):
        if not isinstance(payload[key], dict):
            raise ValueError(f"{key} must be an object.")
    for key in ("limitations", "notes"):
        if not isinstance(payload[key], list):
            raise ValueError(f"{key} must be a list.")
    if payload["validation_type"] == "diagnostic":
        notes.append("diagnostic_only")
    return notes


def _legacy_status(spec: ArtifactSpec, payload: dict[str, Any]) -> tuple[str, list[str]]:
    notes = ["legacy_schema"]
    if spec.validation_id == "taylor_green_2d":
        execution = _normalize_status_for_report(payload.get("execution_status"))
        accuracy = _normalize_status_for_report(payload.get("accuracy_status"))
        return ("failed", notes) if "failed" in {execution, accuracy} else (
            "warning" if "warning" in {execution, accuracy} else "passed",
            notes,
        )
    if spec.validation_id == "taylor_green_convergence_2d":
        acceptance = payload.get("acceptance_statuses", {})
        if not isinstance(acceptance, dict):
            return "failed", notes + ["missing_acceptance_statuses"]
        runtime = _normalize_status_for_report(acceptance.get("runtime_execution"))
        formal = _normalize_status_for_report(acceptance.get("formal_error_convergence"))
        return ("failed", notes) if "failed" in {runtime, formal} else (
            "warning" if "warning" in {runtime, formal} else "passed",
            notes,
        )
    if spec.validation_id == "physical_decay_2d":
        acceptance = payload.get("acceptance_statuses", {})
        if not isinstance(acceptance, dict):
            return "failed", notes + ["missing_acceptance_statuses"]
        runtime = _normalize_status_for_report(acceptance.get("runtime_execution"))
        physical = _normalize_status_for_report(acceptance.get("physical_decay_status"))
        return ("failed", notes) if "failed" in {runtime, physical} else (
            "warning" if "warning" in {runtime, physical} else "passed",
            notes,
        )
    if spec.validation_id == "stress_validation_2d":
        acceptance = payload.get("acceptance_statuses", {})
        if not isinstance(acceptance, dict):
            return "failed", notes + ["missing_acceptance_statuses"]
        runtime = _normalize_status_for_report(acceptance.get("runtime_execution"))
        stress = _normalize_status_for_report(acceptance.get("stress_validation_status"))
        return ("failed", notes) if "failed" in {runtime, stress} else (
            "warning" if "warning" in {runtime, stress} else "passed",
            notes,
        )
    if spec.validation_id == "time_refinement_2d":
        summary = payload.get("summary", {})
        if not isinstance(summary, dict):
            return "failed", notes + ["missing_summary"]
        runtime = _normalize_status_for_report(summary.get("runtime_execution"))
        refine = _normalize_status_for_report(summary.get("time_refinement_status"))
        return ("failed", notes) if "failed" in {runtime, refine} else (
            "warning" if "warning" in {runtime, refine} else "passed",
            notes,
        )
    return "warning", notes + ["unknown_legacy_mapping"]


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _build_md_table_rows(items: list[dict[str, Any]]) -> list[str]:
    rows = [
        "| validation_id | type | status | schema | path | notes |",
        "|---|---|---|---|---|---|",
    ]
    for item in items:
        notes = ",".join(item.get("notes", []))
        rows.append(
            f"| {item['validation_id']} | {item['validation_type']} | {item['status']} | "
            f"{item['schema']} | {item['path']} | {notes} |"
        )
    return rows


def _warning_tokens(payload: dict[str, Any]) -> list[str]:
    tokens: list[str] = []
    warnings = payload.get("warnings", [])
    if isinstance(warnings, list):
        tokens.extend(str(item) for item in warnings)
    summary = payload.get("summary", {})
    if isinstance(summary, dict):
        summary_warnings = summary.get("warnings", [])
        if isinstance(summary_warnings, list):
            tokens.extend(str(item) for item in summary_warnings)
    return sorted(set(tokens))


def _build_discrepancy_analysis(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    analysis: list[dict[str, Any]] = []
    for item in items:
        if item.get("status") != "warning":
            continue
        path = Path(str(item.get("path", "")))
        payload: dict[str, Any] = {}
        if path.exists():
            try:
                payload = _load_json(path)
            except Exception:  # noqa: BLE001
                payload = {}
        validation_id = str(item["validation_id"])
        likely_causes = [
            "warning_status_requires_human_review",
            "diagnostic_evidence_is_not_formal_acceptance",
        ]
        recommended_actions = [
            "inspect_artifact_metrics_before_using_results",
            "keep_scientific_acceptance_as_human_review_required",
        ]
        external_reference = "not_applicable"
        if validation_id in {"forced_turbulence_validation_2d", "resolution_sensitivity_2d"}:
            external_reference = "kraichnan_leith_batchelor_reference_slopes_diagnostic_only"
            likely_causes.extend(
                [
                    "finite_resolution_may_limit_inertial_range",
                    "short_integration_window_may_limit_statistical_stationarity",
                    "forcing_and_dissipation_ranges_may_not_be_well_separated",
                    "two_thirds_dealias_cutoff_limits_high_wavenumber_fit_range",
                ]
            )
            recommended_actions.extend(
                [
                    "run_resolution_sensitivity_matrix_before_escalating_spectral_claims",
                    "treat_k_minus_5_over_3_and_k_minus_3_slopes_as_reference_diagnostics_only",
                ]
            )
        analysis.append(
            {
                "validation_id": validation_id,
                "status": "warning",
                "external_reference": external_reference,
                "warning_tokens": _warning_tokens(payload),
                "likely_causes": likely_causes,
                "recommended_actions": recommended_actions,
                "claim_boundary": "does_not_establish_formal_convergence_or_general_turbulence_validity",
            }
        )
    return analysis


def _build_discrepancy_markdown(analysis: list[dict[str, Any]]) -> list[str]:
    if not analysis:
        return ["No warning-status discrepancy analysis required."]
    rows = [
        "| validation_id | reference context | warning tokens | recommended actions | claim boundary |",
        "|---|---|---|---|---|",
    ]
    for item in analysis:
        rows.append(
            "| "
            + " | ".join(
                [
                    str(item["validation_id"]),
                    str(item["external_reference"]),
                    ",".join(item.get("warning_tokens", [])) or "none",
                    ",".join(item.get("recommended_actions", [])),
                    str(item["claim_boundary"]),
                ]
            )
            + " |"
        )
    return rows


def generate_scientific_validation_report(
    *,
    base_benchmark_dir: str = "outputs/benchmarks",
    output_dir: str = "outputs/reports",
    figures_manifest_path: str = "outputs/figures/figures_manifest.json",
    artifact_specs: list[ArtifactSpec] | None = None,
) -> dict[str, Any]:
    benchmark_root = Path(base_benchmark_dir)
    report_root = Path(output_dir)
    report_root.mkdir(parents=True, exist_ok=True)
    specs = artifact_specs or _default_artifact_specs(benchmark_root)

    sections: dict[str, list[dict[str, Any]]] = {
        "verification": [],
        "validation": [],
        "diagnostic": [],
        "legacy": [],
        "missing": [],
        "invalid": [],
    }
    failed_or_warning_artifacts: list[str] = []
    human_review_required: list[str] = []

    for spec in specs:
        if not spec.path.exists():
            sections["missing"].append(
                {
                    "validation_id": spec.validation_id,
                    "validation_type": spec.validation_type,
                    "status": "missing",
                    "schema": "missing",
                    "path": str(spec.path),
                    "critical": spec.critical,
                    "notes": ["artifact_not_found"],
                }
            )
            continue

        try:
            payload = _load_json(spec.path)
        except Exception as exc:  # noqa: BLE001
            sections["invalid"].append(
                {
                    "validation_id": spec.validation_id,
                    "validation_type": spec.validation_type,
                    "status": "failed",
                    "schema": "invalid",
                    "path": str(spec.path),
                    "critical": spec.critical,
                    "notes": [f"invalid_json:{type(exc).__name__}"],
                }
            )
            failed_or_warning_artifacts.append(spec.validation_id)
            continue

        is_schema = payload.get("schema_version") == "1.0"
        notes: list[str] = []
        if is_schema:
            try:
                notes.extend(_validate_schema_payload(payload))
                status = _normalize_status_for_report(payload.get("status"))
                validation_type = str(payload.get("validation_type"))
            except Exception as exc:  # noqa: BLE001
                sections["invalid"].append(
                    {
                        "validation_id": spec.validation_id,
                        "validation_type": spec.validation_type,
                        "status": "failed",
                        "schema": "1.0_invalid",
                        "path": str(spec.path),
                        "critical": spec.critical,
                        "notes": [f"schema_validation_error:{type(exc).__name__}"],
                    }
                )
                failed_or_warning_artifacts.append(spec.validation_id)
                continue
        else:
            status, legacy_notes = _legacy_status(spec, payload)
            validation_type = spec.validation_type
            notes.extend(legacy_notes)
            sections["legacy"].append(
                {
                    "validation_id": spec.validation_id,
                    "validation_type": validation_type,
                    "status": status,
                    "schema": "legacy",
                    "path": str(spec.path),
                    "critical": spec.critical,
                    "notes": legacy_notes,
                }
            )

        if payload.get("scientific_acceptance") == "human_review_required":
            human_review_required.append(spec.validation_id)
        acceptance = payload.get("acceptance_statuses")
        if isinstance(acceptance, dict) and acceptance.get("scientific_acceptance") == "human_review_required":
            human_review_required.append(spec.validation_id)

        record = {
            "validation_id": spec.validation_id,
            "validation_type": validation_type,
            "status": status,
            "schema": "1.0" if is_schema else "legacy",
            "path": str(spec.path),
            "critical": spec.critical,
            "notes": notes,
        }
        if status in {"failed", "warning"}:
            failed_or_warning_artifacts.append(spec.validation_id)
        sections[validation_type].append(record)

    all_items: list[dict[str, Any]] = []
    for key in ("verification", "validation", "diagnostic", "missing", "invalid"):
        all_items.extend(sections[key])

    counts = {
        "total_artifacts": len(specs),
        "passed": sum(1 for item in all_items if item["status"] == "passed"),
        "warning": sum(1 for item in all_items if item["status"] == "warning"),
        "failed": sum(1 for item in all_items if item["status"] == "failed"),
        "skipped": sum(1 for item in all_items if item["status"] == "skipped"),
        "missing": sum(1 for item in all_items if item["schema"] == "missing"),
        "invalid": sum(1 for item in all_items if item["schema"] in {"invalid", "1.0_invalid"}),
        "legacy": len(sections["legacy"]),
    }

    critical_records = [item for item in all_items if item.get("critical", False)]
    critical_failed = any(
        item["status"] == "failed" or item["schema"] in {"missing", "invalid", "1.0_invalid"}
        for item in critical_records
    )
    critical_missing = any(item["schema"] == "missing" for item in critical_records)

    if critical_failed:
        overall_status = "failed"
    elif critical_missing:
        overall_status = "incomplete"
    elif counts["warning"] > 0 or counts["legacy"] > 0:
        overall_status = "warning"
    else:
        overall_status = "passed"

    discrepancy_analysis = _build_discrepancy_analysis(all_items)

    figures_section: dict[str, Any] = {
        "manifest": figures_manifest_path,
        "status": "missing",
        "generated": [],
        "skipped": [],
        "failed": [],
    }
    manifest_path = Path(figures_manifest_path)
    if manifest_path.exists():
        try:
            manifest = _load_json(manifest_path)
            figures = manifest.get("figures", [])
            if isinstance(figures, list):
                for figure in figures:
                    if not isinstance(figure, dict):
                        continue
                    figure_id = str(figure.get("figure_id", "unknown"))
                    status = str(figure.get("status", "unknown"))
                    if status == "generated":
                        figures_section["generated"].append(figure_id)
                    elif status == "skipped":
                        figures_section["skipped"].append(figure_id)
                    elif status == "failed":
                        figures_section["failed"].append(figure_id)
                figures_section["status"] = "available"
            else:
                figures_section["status"] = "invalid"
                figures_section["failed"].append("figures_manifest_invalid_structure")
        except Exception:
            figures_section["status"] = "invalid"
            figures_section["failed"].append("figures_manifest_invalid_json")

    report_json = {
        "schema_version": "1.0",
        "report_id": "scientific_validation_report",
        "generated_at_utc": _utc_now(),
        "project_scope": CANONICAL_SOLVER_SCOPE,
        "overall_status": overall_status,
        "scientific_acceptance": "human_review_required",
        "claim_policy": {
            "no_3d_claim": True,
            "no_millennium_claim": True,
            "no_formal_proof_claim": True,
            "no_general_navier_stokes_solution_claim": True,
        },
        "summary": counts,
        "sections": sections,
        "human_review_required": sorted(set(human_review_required)),
        "legacy_artifacts": [item["validation_id"] for item in sections["legacy"]],
        "missing_artifacts": [item["validation_id"] for item in sections["missing"]],
        "failed_or_warning_artifacts": sorted(set(failed_or_warning_artifacts)),
        "discrepancy_analysis": discrepancy_analysis,
        "evidence_summary": [
            "This report consolidates deterministic 2D periodic validation artifacts.",
            "Verification, validation, and diagnostic evidence are separated explicitly.",
            "Status interpretation is fail-closed for missing/invalid/failed critical artifacts.",
        ],
        "scientific_limitations": [
            "2d_periodic_scope_only",
            "not_a_3d_result",
            "not_a_millennium_problem_solution",
            "not_a_mathematical_proof",
            "not_a_substitute_for_external_peer_review",
            "numerical_diagnostics_bounded_by_implemented_scenarios",
        ],
        "recommended_next_steps": [
            "Migrate legacy artifacts to schema 1.0.",
            "Generate reproducible figures tied to each validation artifact.",
            "Design docs/web_portal_design.md for the future read-only portal.",
            "Expand comparisons against external references under controlled scope.",
            "Maintain multi-agent scientific audit workflow.",
        ],
        "figures": figures_section,
        "artifacts": {
            "markdown_report": str(report_root / "scientific_validation_report.md"),
            "json_report": str(report_root / "scientific_validation_report.json"),
        },
    }

    markdown_lines = [
        "# Scientific Validation Report",
        "",
        "## Executive Summary",
        f"- Overall status: `{overall_status}`",
        f"- Project scope: `{CANONICAL_SOLVER_SCOPE}`",
        "- Scientific acceptance: `human_review_required`",
        "- No 3D/Millennium/formal proof/general-solution claims.",
        "",
        "## Artifact Summary",
        *_build_md_table_rows(all_items),
        "",
        "## Verification",
        *(_build_md_table_rows(sections["verification"]) if sections["verification"] else ["No verification artifacts detected."]),
        "",
        "## Validation",
        *(_build_md_table_rows(sections["validation"]) if sections["validation"] else ["No validation artifacts detected."]),
        "",
        "## Diagnostics",
        *(_build_md_table_rows(sections["diagnostic"]) if sections["diagnostic"] else ["No diagnostic artifacts detected."]),
        "",
        "## Legacy / Migration Status",
        *(_build_md_table_rows(sections["legacy"]) if sections["legacy"] else ["No legacy artifacts detected."]),
        "",
        "## Missing or Invalid Artifacts",
        *(_build_md_table_rows(sections["missing"] + sections["invalid"]) if (sections["missing"] or sections["invalid"]) else ["No missing or invalid artifacts detected."]),
        "",
        "## Reproducible Figures",
        f"- Manifest: `{figures_manifest_path}`",
        f"- Manifest status: `{figures_section['status']}`",
        f"- Generated: {', '.join(figures_section['generated']) if figures_section['generated'] else 'none'}",
        f"- Skipped: {', '.join(figures_section['skipped']) if figures_section['skipped'] else 'none'}",
        f"- Failed: {', '.join(figures_section['failed']) if figures_section['failed'] else 'none'}",
        "",
        "## Discrepancy Analysis",
        *_build_discrepancy_markdown(discrepancy_analysis),
        "",
        "## Scientific Limitations",
        "- 2D periodic only.",
        "- Not a 3D result.",
        "- Not a Millennium Problem solution.",
        "- Not a mathematical proof.",
        "- Not a substitute for external peer review.",
        "- Numerical diagnostics remain bounded by implemented scenarios.",
        "",
        "## Recommended Next Steps",
        "- Migrate legacy artifacts to schema 1.0.",
        "- Generate reproducible figures.",
        "- Design `docs/web_portal_design.md`.",
        "- Expand comparison against external references.",
        "- Maintain multi-agent audit workflow.",
    ]

    report_json_path = report_root / "scientific_validation_report.json"
    report_md_path = report_root / "scientific_validation_report.md"
    report_json_path.write_text(json.dumps(report_json, indent=2), encoding="utf-8")
    report_md_path.write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")

    return {
        "report_json_path": report_json_path,
        "report_markdown_path": report_md_path,
        "overall_status": overall_status,
    }


def _table_lines(items: list[dict[str, Any]]) -> list[str]:
    lines = ["validation_id | type | status | schema | path"]
    for item in items:
        lines.append(
            f"{item.get('validation_id', 'unknown')} | "
            f"{item.get('validation_type', 'unknown')} | "
            f"{item.get('status', 'unknown')} | "
            f"{item.get('schema', 'unknown')} | "
            f"{item.get('path', 'unknown')}"
        )
    return lines


def _text_page(
    pdf: PdfPages,
    title: str,
    lines: list[str],
    *,
    fontsize: int = 10,
    wrap_width: int = 100,
) -> None:
    fig, ax = plt.subplots(figsize=(8.27, 11.69))
    ax.axis("off")
    fig.text(0.07, 0.965, title, fontsize=15, fontweight="bold", va="top")
    y = 0.93
    for line in lines:
        wrapped_lines = [""]
        if line:
            wrapped_lines = textwrap.wrap(line, width=wrap_width) or [line]
        for wrapped in wrapped_lines:
            fig.text(0.07, y, wrapped, fontsize=fontsize, va="top")
            y -= 0.026
            if y < 0.05:
                pdf.savefig(fig, bbox_inches="tight")
                plt.close(fig)
                fig, ax = plt.subplots(figsize=(8.27, 11.69))
                ax.axis("off")
                fig.text(0.07, 0.965, f"{title} (cont.)", fontsize=15, fontweight="bold", va="top")
                y = 0.93
        if y < 0.05:
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)
            fig, ax = plt.subplots(figsize=(8.27, 11.69))
            ax.axis("off")
            fig.text(0.07, 0.965, f"{title} (cont.)", fontsize=15, fontweight="bold", va="top")
            y = 0.93
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def _status_palette(status: str) -> tuple[str, str]:
    normalized = status.lower()
    if normalized == "passed":
        return "#E8F5E9", "#1B5E20"
    if normalized == "warning":
        return "#FFF8E1", "#8D6E00"
    if normalized in {"failed", "missing"}:
        return "#FFEBEE", "#B71C1C"
    return "#ECEFF1", "#263238"


def _humanize_discrepancy(item: dict[str, Any]) -> list[str]:
    validation_id = str(item.get("validation_id", "unknown_validation"))
    warning_tokens = item.get("warning_tokens", [])
    likely_causes = item.get("likely_causes", [])
    recommended_actions = item.get("recommended_actions", [])
    lines = [
        f"{validation_id}: warning requires conservative interpretation.",
    ]
    if isinstance(warning_tokens, list) and warning_tokens:
        lines.append(f"Warning tokens: {', '.join(str(token) for token in warning_tokens)}.")
    if isinstance(likely_causes, list) and likely_causes:
        lines.append(
            "Likely causes: "
            + "; ".join(str(token).replace("_", " ") for token in likely_causes[:3])
            + "."
        )
    if isinstance(recommended_actions, list) and recommended_actions:
        lines.append(
            "Recommended actions: "
            + "; ".join(str(token).replace("_", " ") for token in recommended_actions[:3])
            + "."
        )
    lines.append(
        "Claim boundary: does not establish formal convergence or general turbulence validity."
    )
    return lines


def _draw_cover_page(
    pdf: PdfPages,
    *,
    generated_at: str,
    overall_status: str,
    scientific_acceptance: str,
) -> None:
    fig, ax = plt.subplots(figsize=(8.27, 11.69))
    ax.axis("off")
    fig.patch.set_facecolor("#F7FAFC")
    fig.text(0.08, 0.92, "Scientific Validation Report", fontsize=24, fontweight="bold", color="#0F172A")
    fig.text(0.08, 0.88, "Human-readable scientific review artifact", fontsize=12, color="#334155")
    fig.text(0.08, 0.83, f"Generated at (UTC): {generated_at}", fontsize=11, color="#334155")
    fig.text(0.08, 0.80, f"Scope: {CANONICAL_SOLVER_SCOPE}", fontsize=11, color="#334155")

    background, text_color = _status_palette(overall_status)
    badge = plt.Rectangle((0.08, 0.72), 0.84, 0.08, transform=fig.transFigure, color=background, ec="#CBD5E1")
    fig.patches.append(badge)
    fig.text(0.10, 0.76, "Overall validation status", fontsize=12, fontweight="bold", color="#1E293B")
    fig.text(0.45, 0.76, overall_status.upper(), fontsize=14, fontweight="bold", color=text_color)
    fig.text(
        0.10,
        0.73,
        f"Scientific acceptance: {scientific_acceptance} (conservative review policy).",
        fontsize=10,
        color="#334155",
    )

    fig.text(0.08, 0.64, "Scope limits", fontsize=12, fontweight="bold", color="#1E293B")
    limits = [
        "2D periodic baseline only.",
        "No 3D Navier-Stokes solution claim.",
        "No Millennium Problem claim.",
        "No mathematical proof claim.",
        "Human scientific review remains required.",
    ]
    y = 0.61
    for limit in limits:
        fig.text(0.10, y, f"- {limit}", fontsize=10.5, color="#334155")
        y -= 0.03
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def _draw_summary_cards(pdf: PdfPages, summary: dict[str, Any], overall_status: str) -> None:
    fig, ax = plt.subplots(figsize=(8.27, 11.69))
    ax.axis("off")
    fig.text(0.08, 0.94, "Executive Summary", fontsize=18, fontweight="bold", color="#0F172A")
    fig.text(
        0.08,
        0.90,
        "Evidence-first snapshot of artifact status for controlled 2D periodic validation.",
        fontsize=11,
        color="#334155",
    )
    labels = [
        ("Total artifacts", int(summary.get("total_artifacts", 0)), "#E3F2FD"),
        ("Passed", int(summary.get("passed", 0)), "#E8F5E9"),
        ("Warning", int(summary.get("warning", 0)), "#FFF8E1"),
        ("Failed", int(summary.get("failed", 0)), "#FFEBEE"),
        ("Missing/Invalid", int(summary.get("missing", 0)) + int(summary.get("invalid", 0)), "#FBE9E7"),
    ]
    positions = [
        (0.08, 0.74), (0.40, 0.74), (0.72, 0.74), (0.24, 0.58), (0.56, 0.58),
    ]
    for (label, value, color), (x, y) in zip(labels, positions):
        box = plt.Rectangle((x, y), 0.20, 0.12, transform=fig.transFigure, color=color, ec="#CBD5E1")
        fig.patches.append(box)
        fig.text(x + 0.02, y + 0.075, label, fontsize=10, color="#334155")
        fig.text(x + 0.02, y + 0.03, str(value), fontsize=20, fontweight="bold", color="#0F172A")
    fig.text(
        0.08,
        0.48,
        f"Overall status remains {overall_status.upper()}. Fail-closed interpretation applies for failed or missing critical evidence.",
        fontsize=10.5,
        color="#334155",
    )
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def _abbreviate_path(path: str, max_length: int = 60) -> str:
    if len(path) <= max_length:
        return path
    return "..." + path[-(max_length - 3):]


def _draw_validation_table(pdf: PdfPages, items: list[dict[str, Any]]) -> None:
    fig, ax = plt.subplots(figsize=(11.69, 8.27))
    ax.axis("off")
    fig.text(0.05, 0.95, "Validation and Artifact Matrix", fontsize=16, fontweight="bold", color="#0F172A")
    rows = []
    for item in items:
        rows.append(
            [
                str(item.get("validation_id", "unknown")),
                str(item.get("validation_type", "unknown")),
                str(item.get("status", "unknown")),
                str(item.get("schema", "unknown")),
                "yes" if bool(item.get("critical", False)) else "no",
                _abbreviate_path(str(item.get("path", "unknown"))),
            ]
        )
    if not rows:
        rows = [["no_artifacts", "-", "-", "-", "-", "-"]]

    table = ax.table(
        cellText=rows,
        colLabels=["Validation", "Type", "Status", "Schema", "Critical", "Artifact path"],
        cellLoc="left",
        colLoc="left",
        loc="center",
        colWidths=[0.22, 0.12, 0.12, 0.10, 0.10, 0.34],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8.5)
    table.scale(1.0, 1.35)

    for col in range(6):
        header_cell = table[(0, col)]
        header_cell.set_facecolor("#E2E8F0")
        header_cell.set_text_props(weight="bold", color="#0F172A")
        header_cell.set_edgecolor("#CBD5E1")

    for idx, row in enumerate(rows, start=1):
        status = row[2]
        bg, fg = _status_palette(status)
        for col in range(6):
            cell = table[(idx, col)]
            cell.set_edgecolor("#E2E8F0")
            if col == 2:
                cell.set_facecolor(bg)
                cell.get_text().set_color(fg)
                cell.get_text().set_weight("bold")
            elif col in {0, 5}:
                cell.set_facecolor("#FAFAFA")
            else:
                cell.set_facecolor("#FFFFFF")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def generate_scientific_validation_pdf(
    *,
    report_json_path: str = "outputs/reports/scientific_validation_report.json",
    output_pdf_path: str = "outputs/reports/scientific_validation_report.pdf",
    fail_closed_on_failed: bool = True,
) -> Path:
    payload = _load_json(Path(report_json_path))
    overall_status = str(payload.get("overall_status", "failed"))
    if fail_closed_on_failed and overall_status == "failed":
        raise RuntimeError(
            "Fail-closed: scientific_validation_report overall_status is failed; PDF not generated."
        )

    generated_at = str(payload.get("generated_at_utc", _utc_now()))
    summary = payload.get("summary", {})
    sections = payload.get("sections", {})
    figures = payload.get("figures", {})
    discrepancy = payload.get("discrepancy_analysis", [])
    limitations = payload.get("scientific_limitations", [])
    evidence = payload.get("evidence_summary", [])
    claim_policy = payload.get("claim_policy", {})

    output_path = Path(output_pdf_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    all_items: list[dict[str, Any]] = []
    for key in ("verification", "validation", "diagnostic", "missing", "invalid"):
        rows = sections.get(key, [])
        if isinstance(rows, list):
            all_items.extend([row for row in rows if isinstance(row, dict)])

    table_lines = _table_lines(all_items) if all_items else ["No artifacts found."]
    artifact_refs = [
        f"JSON report: {report_json_path}",
        f"Markdown report: {str(payload.get('artifacts', {}).get('markdown_report', 'unknown'))}",
        f"Figures manifest: {str(figures.get('manifest', 'unknown'))}",
    ]

    with PdfPages(output_path) as pdf:
        _draw_cover_page(
            pdf,
            generated_at=generated_at,
            overall_status=overall_status,
            scientific_acceptance=str(payload.get("scientific_acceptance", "human_review_required")),
        )
        _draw_summary_cards(pdf, summary if isinstance(summary, dict) else {}, overall_status)
        _draw_validation_table(pdf, all_items)
        _text_page(
            pdf,
            "Conservative Interpretive Analysis",
            [
                "This report consolidates deterministic 2D periodic validation artifacts.",
                "Interpretation is conservative: warnings and diagnostics are not upgraded to formal claims.",
                "Low numerical error or smooth behavior does not imply broad physical validity.",
                "Any failed critical artifact blocks acceptance under fail-closed policy.",
                "",
                "Evidence summary",
                *([str(item) for item in evidence] if isinstance(evidence, list) and evidence else ["No evidence summary entries available."]),
                "",
                "Validation table index (compact)",
                *table_lines[:8],
            ],
            fontsize=10,
            wrap_width=102,
        )
        warnings_lines: list[str] = []
        if isinstance(discrepancy, list) and discrepancy:
            warnings_lines.append("Warning and gap review by validation:")
            warnings_lines.append("")
            for item in discrepancy:
                if not isinstance(item, dict):
                    continue
                warnings_lines.extend(f"- {line}" for line in _humanize_discrepancy(item))
                warnings_lines.append("")
        else:
            warnings_lines.append("No warning-status discrepancy analysis entries were produced.")
        _text_page(pdf, "Warnings and Gaps", warnings_lines, fontsize=10, wrap_width=102)

        limitations_lines = [
            "Explicit limits",
            "- 2D periodic baseline only",
            "- no 3D Navier-Stokes solution claim",
            "- no Millennium Problem claim",
            "- no mathematical proof claim",
            "- human review required when applicable",
            "",
            "Claim policy flags",
            f"- no_3d_claim: {bool(claim_policy.get('no_3d_claim', False))}",
            f"- no_millennium_claim: {bool(claim_policy.get('no_millennium_claim', False))}",
            f"- no_formal_proof_claim: {bool(claim_policy.get('no_formal_proof_claim', False))}",
            f"- no_general_navier_stokes_solution_claim: {bool(claim_policy.get('no_general_navier_stokes_solution_claim', False))}",
            "",
            "Scientific limitation tokens",
            *([f"- {str(item)}" for item in limitations] if isinstance(limitations, list) and limitations else ["- none"]),
            "",
            "Artifact routes",
            *[f"- {line}" for line in artifact_refs],
        ]
        _text_page(pdf, "Limits and Artifact Routes", limitations_lines, fontsize=10, wrap_width=102)
    return output_path
