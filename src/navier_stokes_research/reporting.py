from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from navier_stokes_research.interpretation import classify_relative_difference


TRANSLATIONS = {
    "es": {
        "benchmark_title": "Reporte de benchmark",
        "convergence_title": "Reporte de estudio de convergencia",
        "warnings": "Advertencias",
        "none": "ninguno",
        "final_metrics": "Métricas finales",
        "final_metrics_by_resolution": "Métricas finales por resolución",
        "relative_differences": "Diferencias relativas",
        "estimated_orders": "Órdenes estimados de self-convergence",
        "acceptance_statuses": "Estados de aceptación",
        "scientific_acceptance_note": "Nota de aceptación científica",
        "artifacts": "Artefactos",
        "plot": "Gráfico",
        "validation_status": "estado_de_validación",
        "automatic_diagnosis": "Diagnóstico automático",
        "status": "estado",
        "reasons": "razones",
        "recommendation": "recomendación",
        "validation_checks": "Checks de validación",
        "interpretation": "Interpretación",
        "pass": "aprobado",
        "warn": "advertencia",
        "unknown": "desconocido",
        "acceptable": "aceptable",
        "requires_review": "requiere revisión",
        "artifact_missing": "artefacto faltante",
        "benchmark_disclaimer": (
            "Este reporte resume salidas numéricas y controles de calidad para un baseline 2D; "
            "no es una prueba matemática ni una afirmación de solución formal."
        ),
        "convergence_disclaimer": (
            "Este reporte resume reproducibilidad y consistencia para un baseline 2D. "
            "No es una prueba formal de convergencia numérica."
        ),
        "relative_note": (
            "Diferencias relativas menores sugieren mayor consistencia entre refinamientos. "
            "Una diferencia alta de energía no implica por sí sola un fallo matemático; indica que "
            "conviene revisar comparabilidad de condiciones iniciales, timestep y horizonte físico."
        ),
    },
    "en": {
        "benchmark_title": "Benchmark Report",
        "convergence_title": "Convergence Study Report",
        "warnings": "Warnings",
        "none": "none",
        "final_metrics": "Final Metrics",
        "final_metrics_by_resolution": "Final Metrics by Resolution",
        "relative_differences": "Relative Differences",
        "estimated_orders": "Estimated self-convergence orders",
        "acceptance_statuses": "Acceptance statuses",
        "scientific_acceptance_note": "Scientific acceptance note",
        "artifacts": "Artifacts",
        "plot": "Plot",
        "validation_status": "validation_status",
        "automatic_diagnosis": "Automatic diagnosis",
        "status": "status",
        "reasons": "reasons",
        "recommendation": "recommendation",
        "validation_checks": "Validation checks",
        "interpretation": "Interpretation",
        "pass": "pass",
        "warn": "warn",
        "unknown": "unknown",
        "acceptable": "acceptable",
        "requires_review": "requires review",
        "artifact_missing": "artifact missing",
        "benchmark_disclaimer": (
            "This report summarizes numerical outputs and quality checks for a 2D baseline; "
            "it is not a mathematical proof or a formal solution claim."
        ),
        "convergence_disclaimer": (
            "This report summarizes reproducibility and consistency for a 2D baseline. "
            "It is not a formal proof of numerical convergence."
        ),
        "relative_note": (
            "Smaller relative differences suggest stronger consistency across refinement levels. "
            "A high energy difference is not an automatic mathematical failure; it signals that "
            "initial-condition comparability, timestep, and physical horizon should be reviewed."
        ),
    },
}

STATUS_LABELS = {
    "es": {
        "pass": "aprobado",
        "warn": "advertencia",
        "unknown": "desconocido",
        "aprobado": "aprobado",
        "advertencia": "advertencia",
        "requiere_revision": "requiere_revision",
    },
    "en": {
        "pass": "pass",
        "warn": "warn",
        "unknown": "unknown",
        "aprobado": "pass",
        "advertencia": "warn",
        "requiere_revision": "requires_review",
    },
}


def _t(language: str, key: str) -> str:
    return TRANSLATIONS.get(language, TRANSLATIONS["es"]).get(key, key)


def _status_label(language: str, status: Any) -> str:
    value = str(status)
    return STATUS_LABELS.get(language, STATUS_LABELS["es"]).get(value, value)


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _format_number(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    return _escape(value)


def _safe_relpath(base_dir: Path, target: Path) -> str:
    resolved_base = base_dir.resolve()
    resolved_target = target.resolve()
    try:
        relative = resolved_target.relative_to(resolved_base)
    except ValueError as exc:
        raise ValueError(f"Artifact path escapes output directory: {target}") from exc
    return _escape(relative.as_posix())


def _read_required_json(path: Path, label: str) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required {label}: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _artifact_link(base_dir: Path, path: Path, label: str, language: str) -> str:
    if path.exists():
        rel = _safe_relpath(base_dir, path)
        return f'<a href="{rel}">{_escape(label)}</a>'
    return f"{_escape(label)} ({_escape(_t(language, 'artifact_missing'))})"


def _render_table(rows: list[tuple[str, str]]) -> str:
    body = "\n".join(
        f"<tr><th>{_escape(key)}</th><td>{value}</td></tr>"
        for key, value in rows
    )
    return f"<table>{body}</table>"


def _render_style() -> str:
    return """
<style>
body { font-family: Segoe UI, Arial, sans-serif; margin: 2rem auto; max-width: 1040px; line-height: 1.45; color: #0f172a; }
h1, h2, h3 { color: #0b3b66; }
.disclaimer { padding: 0.75rem; background: #fff8e1; border-left: 4px solid #d97706; }
.diagnosis { padding: 1rem; border: 1px solid #94a3b8; background: #f8fafc; border-radius: 6px; }
.ok { color: #166534; font-weight: 600; }
.warn { color: #b45309; font-weight: 600; }
.review { color: #b91c1c; font-weight: 600; }
table { border-collapse: collapse; width: 100%; margin: 0.75rem 0 1.25rem; }
th, td { border: 1px solid #cbd5e1; padding: 0.4rem 0.55rem; text-align: left; vertical-align: top; }
th { background: #f8fafc; }
code { background: #f1f5f9; padding: 0.1rem 0.25rem; border-radius: 4px; }
ul { margin-top: 0.4rem; }
img { max-width: 100%; border: 1px solid #cbd5e1; }
.missing { color: #b91c1c; font-weight: 600; }
</style>
"""


def _status_class(status: Any) -> str:
    value = str(status)
    if value in {"pass", "aprobado"}:
        return "ok"
    if value in {"requiere_revision"}:
        return "review"
    return "warn"


def _render_diagnosis(quality: dict[str, Any], language: str) -> str:
    reasons = quality.get("reasons", [])
    reasons_html = (
        "<ul>" + "".join(f"<li>{_escape(reason)}</li>" for reason in reasons) + "</ul>"
        if reasons
        else f"<p>{_escape(_t(language, 'none'))}</p>"
    )
    status = quality.get("status", "unknown")
    return f"""
<section class="diagnosis">
<h2>{_escape(_t(language, "automatic_diagnosis"))}</h2>
<p>{_escape(_t(language, "status"))}: <span class="{_status_class(status)}">{_escape(_status_label(language, status))}</span></p>
<h3>{_escape(_t(language, "reasons"))}</h3>
{reasons_html}
<p>{_escape(_t(language, "recommendation"))}: {_escape(quality.get("recommendation", "n/a"))}</p>
</section>
"""


def generate_benchmark_report(output_dir: str | Path, language: str = "es") -> Path:
    base_dir = Path(output_dir)
    summary_path = base_dir / "benchmark_summary.json"
    validation_path = base_dir / "validation_report.json"
    quality_path = base_dir / "benchmark_quality.json"
    metrics_path = base_dir / "metrics.csv"
    plot_path = base_dir / "plots" / "metric_evolution.png"

    summary = _read_required_json(summary_path, "benchmark_summary.json")
    validation = _read_required_json(validation_path, "validation_report.json")
    quality = _read_required_json(quality_path, "benchmark_quality.json")
    final_metrics = summary.get("final_metrics", {})
    warnings = summary.get("warnings", [])
    status = summary.get("validation_status", "unknown")

    metrics_rows = [
        ("energy", _format_number(final_metrics.get("energy", "n/a"))),
        ("enstrophy", _format_number(final_metrics.get("enstrophy", "n/a"))),
        ("max_velocity", _format_number(final_metrics.get("max_velocity", "n/a"))),
        ("cfl", _format_number(final_metrics.get("cfl", "n/a"))),
    ]

    checks_rows = []
    for name, payload in validation.get("checks", {}).items():
        checks_rows.append(
            (
                name,
                f"{_escape(payload.get('ok', 'n/a'))}",
            )
        )

    warnings_html = (
        "<ul>" + "".join(f"<li>{_escape(item)}</li>" for item in warnings) + "</ul>"
        if warnings
        else f"<p>{_escape(_t(language, 'none'))}</p>"
    )

    plot_html = (
        f'<img src="{_safe_relpath(base_dir, plot_path)}" alt="Benchmark metric evolution plot" />'
        if plot_path.exists()
        else f'<p class="missing">metric_evolution.png {_escape(_t(language, "artifact_missing"))}</p>'
    )

    title = _t(language, "benchmark_title")
    content = f"""<!doctype html>
<html lang="{_escape(language)}">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{_escape(title)}</title>
{_render_style()}
</head>
<body>
<h1>{_escape(title)}: {_escape(summary.get("config", {}).get("experiment_name", "unknown"))}</h1>
<p class="disclaimer">{_escape(_t(language, "benchmark_disclaimer"))}</p>
{_render_diagnosis(quality, language)}
<h2>{_escape(_t(language, "validation_checks"))}</h2>
<p>{_escape(_t(language, "validation_status"))}: <span class="{_status_class(status)}">{_escape(_status_label(language, status))}</span></p>
{_render_table(checks_rows)}
<h2>{_escape(_t(language, "warnings"))}</h2>
{warnings_html}
<h2>{_escape(_t(language, "final_metrics"))}</h2>
{_render_table(metrics_rows)}
<h2>{_escape(_t(language, "artifacts"))}</h2>
<ul>
<li>{_artifact_link(base_dir, summary_path, "benchmark_summary.json", language)}</li>
<li>{_artifact_link(base_dir, validation_path, "validation_report.json", language)}</li>
<li>{_artifact_link(base_dir, quality_path, "benchmark_quality.json", language)}</li>
<li>{_artifact_link(base_dir, metrics_path, "metrics.csv", language)}</li>
<li>{_artifact_link(base_dir, plot_path, "plots/metric_evolution.png", language)}</li>
</ul>
<h2>{_escape(_t(language, "plot"))}</h2>
{plot_html}
</body>
</html>
"""
    report_path = base_dir / "report.html"
    report_path.write_text(content, encoding="utf-8")
    return report_path


def generate_convergence_report(output_dir: str | Path, language: str = "es") -> Path:
    base_dir = Path(output_dir)
    summary_path = base_dir / "convergence_summary.json"
    quality_path = base_dir / "convergence_quality.json"
    metrics_path = base_dir / "convergence_metrics.csv"
    plot_path = base_dir / "convergence_comparison.png"
    summary = _read_required_json(summary_path, "convergence_summary.json")
    quality = _read_required_json(quality_path, "convergence_quality.json")

    runs = summary.get("runs", [])
    rel_diffs = summary.get("relative_differences_consecutive", [])
    estimated_orders = summary.get("estimated_self_convergence_orders", [])
    acceptance_statuses = summary.get("acceptance_statuses", {})
    warnings = summary.get("warnings", [])
    created_at = summary.get("created_at_utc", "n/a")
    resolutions = [str(run.get("resolution", "n/a")) for run in runs]

    warnings_html = (
        "<ul>" + "".join(f"<li>{_escape(item)}</li>" for item in warnings) + "</ul>"
        if warnings
        else f"<p>{_escape(_t(language, 'none'))}</p>"
    )

    acceptance_rows = [
        ("runtime_execution", _escape(acceptance_statuses.get("runtime_execution", "n/a"))),
        ("heuristic_consistency", _escape(acceptance_statuses.get("heuristic_consistency", "n/a"))),
        ("scientific_acceptance", _escape(acceptance_statuses.get("scientific_acceptance", "n/a"))),
        (
            "scientific_acceptance_reasons",
            "<ul>"
            + "".join(
                f"<li>{_escape(reason)}</li>"
                for reason in acceptance_statuses.get("scientific_acceptance_reasons", [])
            )
            + "</ul>",
        ),
    ]
    acceptance_table = _render_table(acceptance_rows)

    run_rows = []
    for run in runs:
        final = run.get("final_metrics", {})
        run_rows.append(
            "<tr>"
            f"<td>{_escape(run.get('resolution', 'n/a'))}</td>"
            f"<td>{_escape(_status_label(language, run.get('validation_status', 'n/a')))}</td>"
            f"<td>{_format_number(final.get('energy', 'n/a'))}</td>"
            f"<td>{_format_number(final.get('enstrophy', 'n/a'))}</td>"
            f"<td>{_format_number(final.get('max_velocity', 'n/a'))}</td>"
            f"<td>{_format_number(run.get('cfl_peak', 'n/a'))}</td>"
            "</tr>"
        )
    runs_table = (
        "<table><tr><th>resolution</th><th>estado_de_validación</th><th>final_energy</th>"
        "<th>final_enstrophy</th><th>final_max_velocity</th><th>cfl_peak</th></tr>"
        + "".join(run_rows)
        + "</table>"
    )

    diff_rows = []
    for row in rel_diffs:
        energy_class = classify_relative_difference("energy", row.get("energy"))
        enstrophy_class = classify_relative_difference("enstrophy", row.get("enstrophy"))
        velocity_class = classify_relative_difference("max_velocity", row.get("max_velocity"))
        diff_rows.append(
            "<tr>"
            f"<td>{_escape(row.get('from_resolution', 'n/a'))}</td>"
            f"<td>{_escape(row.get('to_resolution', 'n/a'))}</td>"
            f"<td>{_format_number(row.get('energy', 'n/a'))} ({_escape(energy_class)})</td>"
            f"<td>{_format_number(row.get('enstrophy', 'n/a'))} ({_escape(enstrophy_class)})</td>"
            f"<td>{_format_number(row.get('max_velocity', 'n/a'))} ({_escape(velocity_class)})</td>"
            "</tr>"
        )
    diffs_table = (
        "<table><tr><th>from_resolution</th><th>to_resolution</th><th>rel_diff_energy</th>"
        "<th>rel_diff_enstrophy</th><th>rel_diff_max_velocity</th></tr>"
        + "".join(diff_rows)
        + "</table>"
    )

    order_rows = []
    for row in estimated_orders:
        order_rows.append(
            "<tr>"
            f"<td>{_escape(row.get('coarse_resolution', 'n/a'))}</td>"
            f"<td>{_escape(row.get('medium_resolution', 'n/a'))}</td>"
            f"<td>{_escape(row.get('fine_resolution', 'n/a'))}</td>"
            f"<td>{_format_number(row.get('energy_order', 'n/a'))}</td>"
            f"<td>{_format_number(row.get('enstrophy_order', 'n/a'))}</td>"
            f"<td>{_format_number(row.get('max_velocity_order', 'n/a'))}</td>"
            f"<td>{_escape(row.get('note', 'n/a'))}</td>"
            "</tr>"
        )
    orders_table = (
        "<table><tr><th>coarse</th><th>medium</th><th>fine</th>"
        "<th>energy_order</th><th>enstrophy_order</th><th>max_velocity_order</th><th>note</th></tr>"
        + "".join(order_rows)
        + "</table>"
        if order_rows
        else f"<p>{_escape(_t(language, 'none'))}</p>"
    )

    per_run_links = []
    for run in runs:
        artifacts = run.get("artifacts", {})
        resolution = run.get("resolution", "n/a")
        per_run_links.append(f"<li>resolution n{_escape(resolution)}<ul>")
        for key in ("validation_report_path", "metrics_csv", "plots_dir"):
            artifact_path = artifacts.get(key)
            if artifact_path:
                path_obj = Path(str(artifact_path))
                if not path_obj.is_absolute():
                    path_obj = Path.cwd() / path_obj
                per_run_links.append(
                    f"<li>{_artifact_link(base_dir, path_obj, f'{key} (n{resolution})', language)}</li>"
                )
        per_run_links.append("</ul></li>")

    plot_html = (
        f'<img src="{_safe_relpath(base_dir, plot_path)}" alt="Convergence comparison plot" />'
        if plot_path.exists()
        else f'<p class="missing">convergence_comparison.png {_escape(_t(language, "artifact_missing"))}</p>'
    )

    title = _t(language, "convergence_title")
    content = f"""<!doctype html>
<html lang="{_escape(language)}">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{_escape(title)}</title>
{_render_style()}
</head>
<body>
<h1>{_escape(title)}: {_escape(summary.get("study_name", "unknown"))}</h1>
<p class="disclaimer">{_escape(_t(language, "convergence_disclaimer"))}</p>
{_render_diagnosis(quality, language)}
<p>created_at_utc: <code>{_escape(created_at)}</code></p>
<p>resolutions: <code>{_escape(", ".join(resolutions))}</code></p>
<h2>{_escape(_t(language, "acceptance_statuses"))}</h2>
{acceptance_table}
<p class="disclaimer">{_escape(_t(language, "scientific_acceptance_note"))}: self-convergence order is diagnostic evidence only; formal acceptance still requires an exact/reference solution error study.</p>
<h2>{_escape(_t(language, "warnings"))}</h2>
{warnings_html}
<h2>{_escape(_t(language, "final_metrics_by_resolution"))}</h2>
{runs_table}
<h2>{_escape(_t(language, "relative_differences"))}</h2>
{diffs_table}
<p>{_escape(_t(language, "relative_note"))}</p>
<h2>{_escape(_t(language, "estimated_orders"))}</h2>
{orders_table}
<h2>{_escape(_t(language, "artifacts"))}</h2>
<ul>
<li>{_artifact_link(base_dir, summary_path, "convergence_summary.json", language)}</li>
<li>{_artifact_link(base_dir, quality_path, "convergence_quality.json", language)}</li>
<li>{_artifact_link(base_dir, metrics_path, "convergence_metrics.csv", language)}</li>
<li>{_artifact_link(base_dir, plot_path, "convergence_comparison.png", language)}</li>
{"".join(per_run_links)}
</ul>
<h2>{_escape(_t(language, "plot"))}</h2>
{plot_html}
</body>
</html>
"""
    report_path = base_dir / "report.html"
    report_path.write_text(content, encoding="utf-8")
    return report_path


def generate_reports_index(
    *,
    output_dir: str | Path = "outputs/reports",
    benchmark_report: str | Path = "outputs/benchmarks/baseline_2d_incompressible/report.html",
    convergence_report: str | Path = "outputs/convergence/baseline_resolution_study/report.html",
    language: str = "es",
) -> Path:
    base_dir = Path(output_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    root = base_dir.parent.parent if base_dir.name == "reports" else Path.cwd()
    benchmark_path = Path(benchmark_report)
    convergence_path = Path(convergence_report)
    if not benchmark_path.is_absolute():
        benchmark_path = Path.cwd() / benchmark_path
    if not convergence_path.is_absolute():
        convergence_path = Path.cwd() / convergence_path

    content = f"""<!doctype html>
<html lang="{_escape(language)}">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Research Reports</title>
{_render_style()}
</head>
<body>
<h1>Research Reports</h1>
<ul>
<li>{_artifact_link(root, benchmark_path, "benchmark report", language)}</li>
<li>{_artifact_link(root, convergence_path, "convergence report", language)}</li>
</ul>
</body>
</html>
"""
    index_path = base_dir / "index.html"
    index_path.write_text(content, encoding="utf-8")
    return index_path
