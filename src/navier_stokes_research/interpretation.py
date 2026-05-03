from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BENCHMARK_THRESHOLDS = {
    "energy_ratio_warn": 1.10,
    "enstrophy_ratio_warn": 1.10,
    "cfl_comfort_fraction": 0.50,
    "cfl_warn_fraction": 0.75,
}

CONVERGENCE_THRESHOLDS = {
    "rel_diff_energy_acceptable": 0.25,
    "rel_diff_energy_warn": 0.75,
    "rel_diff_enstrophy_acceptable": 0.20,
    "rel_diff_max_velocity_acceptable": 0.10,
    "cfl_comfort_fraction": 0.50,
    "cfl_warn_fraction": 0.75,
}


def _status_rank(status: str) -> int:
    return {"aprobado": 0, "advertencia": 1, "requiere_revision": 2}[status]


def _max_status(current: str, candidate: str) -> str:
    return candidate if _status_rank(candidate) > _status_rank(current) else current


def _artifact_exists(path: str | Path) -> bool:
    return Path(path).exists()


def interpret_benchmark_quality(
    *,
    summary: dict[str, Any],
    validation_report: dict[str, Any],
    output_dir: str | Path,
) -> dict[str, Any]:
    status = "aprobado"
    reasons: list[str] = []
    output_path = Path(output_dir)

    if summary.get("validation_status") != "pass":
        status = _max_status(status, "requiere_revision")
        reasons.append("validacion_no_aprobada")

    if summary.get("warnings"):
        status = _max_status(status, "advertencia")
        reasons.append("warnings_presentes")

    checks = validation_report.get("checks", {})
    energy_ratio = checks.get("kinetic_energy_trend", {}).get("ratio")
    if energy_ratio is not None and energy_ratio > BENCHMARK_THRESHOLDS["energy_ratio_warn"]:
        status = _max_status(status, "advertencia")
        reasons.append("energia_crece_sobre_umbral")

    enstrophy_ratio = checks.get("enstrophy_trend", {}).get("ratio")
    if enstrophy_ratio is not None and enstrophy_ratio > BENCHMARK_THRESHOLDS["enstrophy_ratio_warn"]:
        status = _max_status(status, "advertencia")
        reasons.append("enstrofia_crece_sobre_umbral")

    cfl_check = checks.get("cfl_margin", {})
    cfl_peak = cfl_check.get("cfl_peak")
    cfl_limit = cfl_check.get("cfl_limit")
    if cfl_peak is not None and cfl_limit:
        if cfl_peak >= BENCHMARK_THRESHOLDS["cfl_warn_fraction"] * cfl_limit:
            status = _max_status(status, "advertencia")
            reasons.append("cfl_cercano_al_limite")

    critical_artifacts = [
        output_path / "benchmark_summary.json",
        output_path / "validation_report.json",
        output_path / "metrics.csv",
    ]
    missing = [str(path) for path in critical_artifacts if not _artifact_exists(path)]
    if missing:
        status = _max_status(status, "requiere_revision")
        reasons.append("faltan_artefactos_criticos")

    if not reasons:
        reasons.append("validacion_y_artefactos_basicos_aprobados")

    return {
        "status": status,
        "reasons": reasons,
        "thresholds": BENCHMARK_THRESHOLDS,
        "recommendation": _benchmark_recommendation(status, reasons),
        "missing_critical_artifacts": missing,
    }


def _benchmark_recommendation(status: str, reasons: list[str]) -> str:
    if status == "requiere_revision":
        return "Revisar validacion, artefactos criticos y estabilidad antes de usar este benchmark como referencia."
    if "cfl_cercano_al_limite" in reasons:
        return "Reducir dt o revisar el margen CFL si se planean corridas mas largas."
    return "Mantener este benchmark como referencia reproducible y ampliar solo con cambios controlados."


def interpret_convergence_quality(
    *,
    summary: dict[str, Any],
    output_dir: str | Path,
) -> dict[str, Any]:
    status = "aprobado"
    reasons: list[str] = []
    output_path = Path(output_dir)

    runs = summary.get("runs", [])
    if len(runs) <= 2:
        status = _max_status(status, "advertencia")
        reasons.append("solo_dos_resoluciones")

    for run in runs:
        if run.get("validation_status") != "pass":
            status = _max_status(status, "requiere_revision")
            reasons.append(f"resolucion_{run.get('resolution')}_no_aprueba_validacion")

    for item in summary.get("relative_differences_consecutive", []):
        energy = item.get("energy")
        enstrophy = item.get("enstrophy")
        max_velocity = item.get("max_velocity")

        if energy is not None and energy > CONVERGENCE_THRESHOLDS["rel_diff_energy_warn"]:
            status = _max_status(status, "requiere_revision")
            reasons.append("diferencia_relativa_energia_muy_alta")
        elif energy is not None and energy > CONVERGENCE_THRESHOLDS["rel_diff_energy_acceptable"]:
            status = _max_status(status, "advertencia")
            reasons.append("diferencia_relativa_energia_alta")

        if enstrophy is not None and enstrophy > CONVERGENCE_THRESHOLDS["rel_diff_enstrophy_acceptable"]:
            status = _max_status(status, "advertencia")
            reasons.append("diferencia_relativa_enstrofia_alta")

        if max_velocity is not None and max_velocity > CONVERGENCE_THRESHOLDS["rel_diff_max_velocity_acceptable"]:
            status = _max_status(status, "advertencia")
            reasons.append("diferencia_relativa_velocidad_maxima_alta")

    for run in runs:
        cfl_peak = run.get("cfl_peak")
        cfl_limit = run.get("config", {}).get("time", {}).get("cfl_safety")
        if cfl_peak is not None and cfl_limit:
            if cfl_peak >= CONVERGENCE_THRESHOLDS["cfl_warn_fraction"] * cfl_limit:
                status = _max_status(status, "advertencia")
                reasons.append(f"cfl_alto_resolucion_{run.get('resolution')}")

    expected_artifacts = [
        output_path / "convergence_summary.json",
        output_path / "convergence_metrics.csv",
        output_path / "convergence_comparison.png",
    ]
    missing = [str(path) for path in expected_artifacts if not _artifact_exists(path)]
    if missing:
        status = _max_status(status, "requiere_revision")
        reasons.append("faltan_artefactos_esperados")

    reasons = list(dict.fromkeys(reasons))
    if not reasons:
        reasons.append("metricas_relativas_y_validaciones_en_rango_heuristico")

    return {
        "status": status,
        "reasons": reasons,
        "thresholds": CONVERGENCE_THRESHOLDS,
        "recommendation": _convergence_recommendation(status, reasons),
        "missing_expected_artifacts": missing,
    }


def classify_relative_difference(metric: str, value: float | None) -> str:
    if value is None:
        return "desconocido"
    if metric == "energy":
        if value > CONVERGENCE_THRESHOLDS["rel_diff_energy_warn"]:
            return "requiere_revision"
        if value > CONVERGENCE_THRESHOLDS["rel_diff_energy_acceptable"]:
            return "advertencia"
        return "aceptable"
    if metric == "enstrophy":
        return (
            "advertencia"
            if value > CONVERGENCE_THRESHOLDS["rel_diff_enstrophy_acceptable"]
            else "aceptable"
        )
    if metric == "max_velocity":
        return (
            "advertencia"
            if value > CONVERGENCE_THRESHOLDS["rel_diff_max_velocity_acceptable"]
            else "aceptable"
        )
    return "desconocido"


def _convergence_recommendation(status: str, reasons: list[str]) -> str:
    if "diferencia_relativa_energia_muy_alta" in reasons:
        return "La energia final cambia demasiado entre resoluciones; revisar comparabilidad de condiciones iniciales y estudio de timestep."
    if "solo_dos_resoluciones" in reasons:
        return "Agregar una tercera resolucion para estimar tendencia."
    if status == "aprobado":
        return "Las diferencias de velocidad maxima son bajas; esta metrica parece estable en el baseline actual."
    return "Revisar las metricas con advertencia antes de ampliar el estudio."


def write_quality_report(path: str | Path, report: dict[str, Any]) -> None:
    destination = Path(path)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
