# Navier-Stokes Research Agent: Contrato Conceptual

## Alcance

Este documento define contratos JSON conceptuales para integración futura con CommandIA. No es implementación runtime, no agrega validadores ejecutables y no modifica solver ni CLI.

## Reglas globales de contrato

- Todos los contratos son evidence-first y audit-friendly.
- Campos mínimos faltantes implican rechazo fail-closed.
- Valores físicamente inválidos o no reproducibles implican rechazo fail-closed.
- `null` o tipos incompatibles en campos obligatorios implican rechazo fail-closed.
- Versionado semántico de contrato recomendado mediante `schema_version`.

## 1) ResearchIntent

### Propósito

Representar la intención inicial del usuario para una investigación computacional, con límites y criterios explícitos.

### Campos mínimos

- `intent_id` (string)
- `created_at_utc` (string ISO-8601)
- `requester` (string)
- `objective` (string)
- `constraints` (array[string])
- `acceptance_criteria` (array[string])
- `schema_version` (string)

### Ejemplo JSON

```json
{
  "intent_id": "ri-2026-05-03-001",
  "created_at_utc": "2026-05-03T20:00:00Z",
  "requester": "research_user",
  "objective": "Evaluar estabilidad de un setup 2D periódico controlado",
  "constraints": [
    "no cambiar solver",
    "no claims matemáticos",
    "reproducibilidad obligatoria"
  ],
  "acceptance_criteria": [
    "artefactos versionados",
    "métricas finitas",
    "reporte auditable"
  ],
  "schema_version": "0.1.0"
}
```

### Reglas básicas de validación

- `objective` no puede ser vacío.
- `constraints` y `acceptance_criteria` deben contener al menos un elemento.

### Fail-closed esperado

Si falta un campo mínimo o existe ambigüedad crítica en el objetivo, el proceso no avanza a planificación.

## 2) ExperimentPlan

### Propósito

Describir una propuesta de experimento reproducible y acotada, derivada de `ResearchIntent`.

### Campos mínimos

- `plan_id` (string)
- `intent_id` (string)
- `hypothesis` (string)
- `config_reference` (string)
- `run_matrix` (array[object])
- `safety_checks_required` (array[string])
- `rollback_steps` (array[string])
- `schema_version` (string)

### Ejemplo JSON

```json
{
  "plan_id": "ep-2026-05-03-001",
  "intent_id": "ri-2026-05-03-001",
  "hypothesis": "Con parámetros estables, las métricas permanecen finitas en el horizonte definido",
  "config_reference": "configs/baseline_random.json",
  "run_matrix": [
    {
      "label": "baseline_run",
      "dt": 0.0015,
      "steps": 160
    }
  ],
  "safety_checks_required": [
    "viscosity_positive",
    "cfl_margin_positive",
    "nan_inf_fail_fast"
  ],
  "rollback_steps": [
    "revertir cambios documentales de la iteración",
    "no publicar resultados parciales"
  ],
  "schema_version": "0.1.0"
}
```

### Reglas básicas de validación

- `run_matrix` no puede estar vacío.
- Cada entrada de `run_matrix` debe tener identificador (`label`) y parámetros numéricos válidos.

### Fail-closed esperado

Si falta trazabilidad con `intent_id` o el plan no tiene rollback explícito, se rechaza.

## 3) SafetyAssessment

### Propósito

Registrar evaluación de seguridad previa a ejecución y su decisión.

### Campos mínimos

- `assessment_id` (string)
- `plan_id` (string)
- `status` (string: `approved` o `rejected`)
- `checks` (array[object])
- `reviewed_by` (string)
- `reviewed_at_utc` (string ISO-8601)
- `schema_version` (string)

### Ejemplo JSON

```json
{
  "assessment_id": "sa-2026-05-03-001",
  "plan_id": "ep-2026-05-03-001",
  "status": "approved",
  "checks": [
    {"name": "viscosity_positive", "ok": true},
    {"name": "time_step_positive", "ok": true},
    {"name": "domain_consistency", "ok": true}
  ],
  "reviewed_by": "numerical_safety_gate",
  "reviewed_at_utc": "2026-05-03T20:10:00Z",
  "schema_version": "0.1.0"
}
```

### Reglas básicas de validación

- `status=rejected` obligatorio si al menos un check crítico falla.
- Cada check debe explicitar `name` y `ok`.

### Fail-closed esperado

Ante checks incompletos, contradictorios o no finitos, la ejecución no se autoriza.

## 4) SimulationRunRequest

### Propósito

Solicitar una ejecución concreta bajo un plan y evaluación de seguridad aprobados.

### Campos mínimos

- `run_request_id` (string)
- `plan_id` (string)
- `assessment_id` (string)
- `resolved_config` (object)
- `expected_artifacts` (array[string])
- `schema_version` (string)

### Ejemplo JSON

```json
{
  "run_request_id": "srr-2026-05-03-001",
  "plan_id": "ep-2026-05-03-001",
  "assessment_id": "sa-2026-05-03-001",
  "resolved_config": {
    "grid": {"nx": 64, "ny": 64},
    "physics": {"viscosity": 0.001},
    "time": {"dt": 0.0015, "steps": 160}
  },
  "expected_artifacts": [
    "metrics.csv",
    "resolved_config.json",
    "validation_report.json"
  ],
  "schema_version": "0.1.0"
}
```

### Reglas básicas de validación

- `assessment_id` debe referir una evaluación aprobada.
- `resolved_config` debe estar completo para reproducibilidad.

### Fail-closed esperado

Si no existe vínculo verificable con una aprobación de seguridad, la corrida se bloquea.

## 5) SimulationRunResult

### Propósito

Capturar resultado verificable de una corrida ejecutada.

### Campos mínimos

- `run_result_id` (string)
- `run_request_id` (string)
- `status` (string: `completed` o `failed`)
- `artifacts` (object)
- `final_metrics` (object)
- `reproducibility_signature` (string)
- `schema_version` (string)

### Ejemplo JSON

```json
{
  "run_result_id": "srrs-2026-05-03-001",
  "run_request_id": "srr-2026-05-03-001",
  "status": "completed",
  "artifacts": {
    "metrics_csv": "outputs/.../metrics.csv",
    "validation_report": "outputs/.../validation_report.json"
  },
  "final_metrics": {
    "energy": 0.17,
    "enstrophy": 0.28,
    "max_velocity": 0.91,
    "cfl": 0.22
  },
  "reproducibility_signature": "seed=2026|nx=64|ny=64|dt=0.0015|steps=160",
  "schema_version": "0.1.0"
}
```

### Reglas básicas de validación

- `status=completed` requiere artefactos y métricas presentes y finitos.
- `status=failed` requiere razón técnica explícita.

### Fail-closed esperado

Si faltan artefactos críticos o hay NaN/Inf en métricas, se marca `failed`.

## 6) MetricsAnalysis

### Propósito

Consolidar interpretación de métricas y señales de calidad de una o más corridas.

### Campos mínimos

- `analysis_id` (string)
- `input_run_results` (array[string])
- `checks_summary` (object)
- `warnings` (array[string])
- `conclusion` (string)
- `schema_version` (string)

### Ejemplo JSON

```json
{
  "analysis_id": "ma-2026-05-03-001",
  "input_run_results": ["srrs-2026-05-03-001"],
  "checks_summary": {
    "finite_metrics": true,
    "cfl_margin_positive": true,
    "diffusion_margin_positive": true
  },
  "warnings": [],
  "conclusion": "Se observaron métricas finitas en el caso controlado evaluado",
  "schema_version": "0.1.0"
}
```

### Reglas básicas de validación

- `input_run_results` no puede ser vacío.
- `conclusion` debe estar respaldada por `checks_summary` y `warnings`.

### Fail-closed esperado

Si no hay trazabilidad a resultados concretos o faltan checks críticos, no se emite análisis aprobable.

## 7) ResearchFinding

### Propósito

Documentar un hallazgo técnico/científico provisional para revisión humana.

### Campos mínimos

- `finding_id` (string)
- `analysis_id` (string)
- `claim_level` (string: `observational` recomendado)
- `statement` (string)
- `evidence_refs` (array[string])
- `limitations` (array[string])
- `requires_human_review` (boolean)
- `schema_version` (string)

### Ejemplo JSON

```json
{
  "finding_id": "rf-2026-05-03-001",
  "analysis_id": "ma-2026-05-03-001",
  "claim_level": "observational",
  "statement": "En este setup 2D controlado no se detectaron métricas no finitas",
  "evidence_refs": [
    "outputs/.../metrics.csv",
    "outputs/.../validation_report.json"
  ],
  "limitations": [
    "caso 2D periódico",
    "horizonte temporal finito",
    "no extrapolable a prueba formal 3D"
  ],
  "requires_human_review": true,
  "schema_version": "0.1.0"
}
```

### Reglas básicas de validación

- `claim_level` no puede implicar prueba teórica.
- `requires_human_review` debe ser `true` para hallazgos científicos.

### Fail-closed esperado

Si el hallazgo no tiene evidencia trazable o omite limitaciones, se rechaza publicación.

## Cláusula de no sobreclaiming

Estos contratos no autorizan afirmaciones theorem-level. Toda salida del agente se considera evidencia computacional contextual y requiere revisión humana antes de cualquier claim científico.
