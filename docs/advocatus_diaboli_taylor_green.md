# Advocatus Diaboli: Auditoría Inicial de Taylor-Green 2D

## 1. Propósito de la revisión

Esta revisión adopta el rol de *Advocatus Diaboli*: cuestionar resultados y supuestos, no validarlos automáticamente.

El objetivo es reducir riesgo de sobreinterpretación en la validación Taylor-Green 2D recientemente incorporada.

Taylor-Green 2D es un benchmark controlado para verificación numérica localizada. No constituye evidencia de resolución del problema 3D de Navier-Stokes ni una demostración matemática.

## 2. Riesgos de falso positivo

- Métricas finitas no implican precisión suficiente.
- `status=passed` puede reflejar ejecución técnicamente completada, no exactitud científica aceptable.
- Puede haber error relevante por resolución espacial insuficiente.
- Puede haber error relevante por paso temporal (`dt`) inadecuado.
- Puede haber sesgo por suposición de frontera periódica fuera de contexto.
- Puede haber error de discretización aunque no aparezcan NaN/Inf.
- Puede haber desalineación entre solución analítica y representación discreta en grilla/tiempo.

## 3. Preguntas críticas obligatorias

1. ¿Qué significa exactamente `passed` en el JSON actual?
2. ¿Existe tolerancia numérica explícita para aceptar/rechazar precisión?
3. ¿Los errores `L2` y `L∞` son aceptables para la resolución usada?
4. ¿Se comparó la solución exacta en `t=0` y en `t>0` con criterios cuantitativos explícitos?
5. ¿La energía decae de forma consistente con la tendencia analítica esperada?
6. ¿La validación distingue entre “ejecución exitosa” y “precisión aceptable”?

## 4. Recomendaciones para la siguiente iteración

- Separar `execution_status` de `accuracy_status`.
- Agregar tolerancias configurables para `L2`, `L∞` y error relativo.
- Agregar comparación en múltiples resoluciones para evaluar robustez.
- Agregar validación explícita de decaimiento de energía.
- Reportar siempre resolución, `dt`, número de pasos y norma inicial/final.
- Mantener el disclaimer: este flujo no prueba existencia/suavidad global 3D.

## 5. Criterios mínimos para aceptar científicamente una corrida Taylor-Green

- Métricas finitas.
- Tolerancias explícitas y justificadas.
- Reproducibilidad verificable.
- Configuración completa persistida en JSON.
- Comparación contra baseline definido.
- Revisión humana previa a conclusiones científicas.

## 6. Límites explícitos

- No es prueba matemática.
- No es validación 3D.
- No descarta singularidades.
- No demuestra suavidad global.
- No reemplaza análisis teórico ni revisión científica externa.

## Evidencia usada en esta revisión

- Código de validación: `src/navier_stokes_research/taylor_green.py`.
- Pruebas existentes: `tests/test_taylor_green_validation.py`.
- Artefacto observado: `outputs/benchmarks/taylor_green_2d/taylor_green_validation.json`.

Observación puntual: el estado `passed` actual se decide por finitud de métricas, no por umbral explícito de precisión. Este comportamiento puede ser útil para hardening operativo, pero no basta para aceptación científica.
