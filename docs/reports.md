# Static HTML Reports

This repository generates local static HTML reports for benchmark and convergence runs.

## Scope

- No web server is required.
- No CDN or external JavaScript is used.
- No network access is required.
- Reports can be opened directly in a browser by double-clicking `report.html`.
- Reports are generated in Spanish by default.

## Expected outputs

- Benchmark report:
  - `outputs/benchmarks/baseline_2d_incompressible/report.html`
  - `outputs/benchmarks/baseline_2d_incompressible/benchmark_quality.json`
- Convergence report:
  - `outputs/convergence/baseline_resolution_study/report.html`
  - `outputs/convergence/baseline_resolution_study/convergence_quality.json`
- Optional index:
  - `outputs/reports/index.html`

## Design notes

- Reports are generated from existing JSON/CSV/PNG artifacts.
- Dynamic values are HTML-escaped before rendering.
- Missing non-critical artifacts are displayed as `artifact missing` instead of failing report generation.
- Missing critical JSON (`benchmark_summary.json`, `validation_report.json`, `convergence_summary.json`) raises explicit errors.
- Quality JSON files store heuristic diagnoses for quick review and downstream automation.
