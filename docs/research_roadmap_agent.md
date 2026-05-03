# Navier-Stokes Research Agent: Roadmap de Implementación

## Alcance de esta iteración

Esta iteración cubre únicamente documentación arquitectónica y contratos conceptuales.

Fuera de alcance en esta iteración:

- implementación runtime del agente,
- cambios en solver,
- cambios en CLI,
- ejecución automática adicional de pipelines,
- integración real con HPC/GPU,
- claims matemáticos sobre el problema 3D de Navier-Stokes.

## Fase 0: Documentación y contratos

### Objetivo

Establecer base conceptual auditable para integración futura con CommandIA.

### Entregables

- `docs/agent_architecture.md`
- `docs/agent_contract.md`
- `docs/research_roadmap_agent.md`

### Criterios de aceptación

- Documentos claros, consistentes y reproducibles.
- Disclaimers científicos explícitos.
- Cero cambios runtime.

## Fase 1: Agente local read-only

### Objetivo

Inspección pasiva de `configs/`, `outputs/` y artefactos existentes.

### Criterios de aceptación

- No ejecuta simulaciones.
- No modifica archivos.
- Reporta hallazgos con trazabilidad.

## Fase 2: Propuesta de experimentos sin ejecución

### Objetivo

Generar planes de experimento y checklists de seguridad sin correr solver.

### Criterios de aceptación

- Planes con hipótesis, criterios de aceptación y rollback.
- Rechazo fail-closed ante parámetros ambiguos.

## Fase 3: Ejecución local controlada con Safety Gate

### Objetivo

Permitir ejecuciones locales aprobadas bajo precondiciones numéricas explícitas.

### Criterios de aceptación

- Gate bloquea corridas inválidas.
- Cada corrida deja rastro de configuración y artefactos.
- Sin cambios no autorizados en componentes críticos.

## Fase 4: Análisis comparativo y reportes

### Objetivo

Agregar análisis entre corridas y consolidación de reportes reproducibles.

### Criterios de aceptación

- Comparativas trazables y auditables.
- Reportes con limitaciones explícitas.
- Sin sobreclaiming.

## Fase 5: Extensión 3D experimental (sin claims matemáticos)

### Objetivo

Explorar prototipos experimentales 3D solo como investigación computacional.

### Criterios de aceptación

- Etiquetado explícito de experimental.
- Límites y supuestos documentados.
- Cero afirmaciones theorem-level.

## Fase 6: Integración HPC/GPU opcional

### Objetivo

Escalar ejecuciones bajo control estricto de reproducibilidad.

### Criterios de aceptación

- Entornos versionados y trazables.
- Mecanismos de fallback local.
- Evidencia comparativa CPU/HPC documentada.

## Fase 7: Revisión científica externa

### Objetivo

Someter metodología y resultados a revisión independiente.

### Criterios de aceptación

- Paquete de evidencia reproducible.
- Protocolos de validación transparentes.
- Retroalimentación incorporada con trazabilidad.

## Riesgos técnicos

- Deriva de contratos entre control plane y execution engine.
- Falta de trazabilidad entre intención, plan y artefactos.
- Resultados no reproducibles por configuración incompleta.
- Acoplamiento prematuro a infraestructura externa.

## Riesgos científicos

- Interpretar señales numéricas como validez general.
- Extrapolar resultados fuera del dominio/modelo evaluado.
- Omitir análisis de sensibilidad temporal/espacial.

## Riesgos de overclaiming

- Confundir evidencia computacional con demostración matemática.
- Comunicar conclusiones sin revisión humana independiente.
- Ignorar límites explícitos del caso 2D periódico.

## Límites explícitos

- El agente no demuestra existencia/suavidad global 3D.
- El agente no sustituye revisión científica humana.
- El agente organiza, audita y asiste investigación computacional.

## Plan de rollback

- Revertir solo archivos documentales agregados en la iteración.
- No alterar ramas/historial fuera del cambio controlado.
- No publicar commit si validación requerida falla por cambios introducidos.

## Gobernanza operativa

- Evidence-first: toda conclusión debe apuntar a artefactos verificables.
- Fail-closed: campos faltantes o inconsistencias críticas bloquean avance.
- Audit-friendly: decisiones, supuestos y estados deben quedar registrados.
- Reproducibility-first: sin configuración resoluble no hay ejecución válida.
