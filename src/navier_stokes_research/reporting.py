from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)


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


def _artifact_link(base_dir: Path, path: Path, label: str) -> str:
    if path.exists():
        rel = _safe_relpath(base_dir, path)
        return f'<a href="{rel}">{_escape(label)}</a>'
    return f"{_escape(label)} (artifact missing)"


def _render_table(rows: list[tuple[str, str]]) -> str:
    body = "\n".join(
        f"<tr><th>{_escape(key)}</th><td>{value}</td></tr>"
        for key, value in rows
    )
    return f"<table>{body}</table>"


def _render_style() -> str:
    return """
<style>
body { font-family: Segoe UI, Arial, sans-serif; margin: 2rem auto; max-width: 960px; line-height: 1.45; color: #0f172a; }
h1, h2, h3 { color: #0b3b66; }
.disclaimer { padding: 0.75rem; background: #fff8e1; border-left: 4px solid #d97706; }
.ok { color: #166534; font-weight: 600; }
.warn { color: #b45309; font-weight: 600; }
table { border-collapse: collapse; width: 100%; margin: 0.75rem 0 1.25rem; }
th, td { border: 1px solid #cbd5e1; padding: 0.4rem 0.55rem; text-align: left; vertical-align: top; }
th { background: #f8fafc; width: 30%; }
code { background: #f1f5f9; padding: 0.1rem 0.25rem; border-radius: 4px; }
ul { margin-top: 0.4rem; }
img { max-width: 100%; border: 1px solid #cbd5e1; }
.missing { color: #b91c1c; font-weight: 600; }
</style>
"""


def generate_benchmark_report(output_dir: str | Path) -> Path:
    base_dir = Path(output_dir)
    summary_path = base_dir / "benchmark_summary.json"
    validation_path = base_dir / "validation_report.json"
    metrics_path = base_dir / "metrics.csv"
    plot_path = base_dir / "plots" / "metric_evolution.png"

    summary = _read_required_json(summary_path, "benchmark_summary.json")
    validation = _read_required_json(validation_path, "validation_report.json")
    final_metrics = summary.get("final_metrics", {})
    warnings = summary.get("warnings", [])
    status = summary.get("validation_status", "unknown")
    status_class = "ok" if status == "pass" else "warn"

    metrics_rows = [
        ("energy", _escape(final_metrics.get("energy", "n/a"))),
        ("enstrophy", _escape(final_metrics.get("enstrophy", "n/a"))),
        ("max_velocity", _escape(final_metrics.get("max_velocity", "n/a"))),
        ("cfl", _escape(final_metrics.get("cfl", "n/a"))),
    ]

    warnings_html = (
        "<ul>" + "".join(f"<li>{_escape(item)}</li>" for item in warnings) + "</ul>"
        if warnings
        else "<p>none</p>"
    )

    plot_html = (
        f'<img src="{_safe_relpath(base_dir, plot_path)}" alt="Benchmark metric evolution plot" />'
        if plot_path.exists()
        else '<p class="missing">metric_evolution.png artifact missing</p>'
    )

    content = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Benchmark Report</title>
{_render_style()}
</head>
<body>
<h1>Benchmark Report: {_escape(summary.get("config", {}).get("experiment_name", "unknown"))}</h1>
<p class="disclaimer">Scientific disclaimer: this report summarizes numerical experiment outputs and quality checks for a 2D baseline; it is not a mathematical proof or a formal solution claim.</p>
<h2>Validation</h2>
<p>validation_status: <span class="{status_class}">{_escape(status)}</span></p>
<p>Validation checks counted: {_escape(len(validation.get("checks", {})))}</p>
<h2>Warnings</h2>
{warnings_html}
<h2>Final Metrics</h2>
{_render_table(metrics_rows)}
<h2>Artifacts</h2>
<ul>
<li>{_artifact_link(base_dir, summary_path, "benchmark_summary.json")}</li>
<li>{_artifact_link(base_dir, validation_path, "validation_report.json")}</li>
<li>{_artifact_link(base_dir, metrics_path, "metrics.csv")}</li>
<li>{_artifact_link(base_dir, plot_path, "plots/metric_evolution.png")}</li>
</ul>
<h2>Plot</h2>
{plot_html}
</body>
</html>
"""
    report_path = base_dir / "report.html"
    report_path.write_text(content, encoding="utf-8")
    return report_path


def generate_convergence_report(output_dir: str | Path) -> Path:
    base_dir = Path(output_dir)
    summary_path = base_dir / "convergence_summary.json"
    metrics_path = base_dir / "convergence_metrics.csv"
    plot_path = base_dir / "convergence_comparison.png"
    summary = _read_required_json(summary_path, "convergence_summary.json")

    runs = summary.get("runs", [])
    rel_diffs = summary.get("relative_differences_consecutive", [])
    warnings = summary.get("warnings", [])
    created_at = summary.get("created_at_utc", "n/a")
    resolutions = [str(run.get("resolution", "n/a")) for run in runs]

    warnings_html = (
        "<ul>" + "".join(f"<li>{_escape(item)}</li>" for item in warnings) + "</ul>"
        if warnings
        else "<p>none</p>"
    )

    run_rows = []
    for run in runs:
        final = run.get("final_metrics", {})
        run_rows.append(
            "<tr>"
            f"<td>{_escape(run.get('resolution', 'n/a'))}</td>"
            f"<td>{_escape(run.get('validation_status', 'n/a'))}</td>"
            f"<td>{_escape(final.get('energy', 'n/a'))}</td>"
            f"<td>{_escape(final.get('enstrophy', 'n/a'))}</td>"
            f"<td>{_escape(final.get('max_velocity', 'n/a'))}</td>"
            f"<td>{_escape(run.get('cfl_peak', 'n/a'))}</td>"
            "</tr>"
        )
    runs_table = (
        "<table><tr><th>resolution</th><th>validation_status</th><th>final_energy</th>"
        "<th>final_enstrophy</th><th>final_max_velocity</th><th>cfl_peak</th></tr>"
        + "".join(run_rows)
        + "</table>"
    )

    diff_rows = []
    for row in rel_diffs:
        diff_rows.append(
            "<tr>"
            f"<td>{_escape(row.get('from_resolution', 'n/a'))}</td>"
            f"<td>{_escape(row.get('to_resolution', 'n/a'))}</td>"
            f"<td>{_escape(row.get('energy', 'n/a'))}</td>"
            f"<td>{_escape(row.get('enstrophy', 'n/a'))}</td>"
            f"<td>{_escape(row.get('max_velocity', 'n/a'))}</td>"
            "</tr>"
        )
    diffs_table = (
        "<table><tr><th>from_resolution</th><th>to_resolution</th><th>rel_diff_energy</th>"
        "<th>rel_diff_enstrophy</th><th>rel_diff_max_velocity</th></tr>"
        + "".join(diff_rows)
        + "</table>"
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
                    f"<li>{_artifact_link(base_dir, path_obj, f'{key} (n{resolution})')}</li>"
                )
        per_run_links.append("</ul></li>")

    plot_html = (
        f'<img src="{_safe_relpath(base_dir, plot_path)}" alt="Convergence comparison plot" />'
        if plot_path.exists()
        else '<p class="missing">convergence_comparison.png artifact missing</p>'
    )

    content = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Convergence Report</title>
{_render_style()}
</head>
<body>
<h1>Convergence Study Report: {_escape(summary.get("study_name", "unknown"))}</h1>
<p class="disclaimer">This report is a reproducibility and consistency snapshot for a 2D baseline. It is not a formal proof of numerical convergence.</p>
<p>created_at_utc: <code>{_escape(created_at)}</code></p>
<p>resolutions: <code>{_escape(", ".join(resolutions))}</code></p>
<h2>Warnings</h2>
{warnings_html}
<h2>Final Metrics by Resolution</h2>
{runs_table}
<h2>Relative Differences (Consecutive Resolutions)</h2>
{diffs_table}
<p>Interpretation: smaller relative differences suggest stronger consistency across refinement levels, but this alone does not establish formal convergence order.</p>
<h2>Artifacts</h2>
<ul>
<li>{_artifact_link(base_dir, summary_path, "convergence_summary.json")}</li>
<li>{_artifact_link(base_dir, metrics_path, "convergence_metrics.csv")}</li>
<li>{_artifact_link(base_dir, plot_path, "convergence_comparison.png")}</li>
{"".join(per_run_links)}
</ul>
<h2>Plot</h2>
{plot_html}
</body>
</html>
"""
    report_path = base_dir / "report.html"
    report_path.write_text(content, encoding="utf-8")
    return report_path
