# Advocatus Diaboli: Auditoria Inicial de Taylor-Green 2D

## Proposito

Este documento define una revision critica inicial para la validacion Taylor-Green 2D. El rol de Advocatus Diaboli es cuestionar resultados y supuestos, no confirmarlos automaticamente.

Taylor-Green 2D es un benchmark controlado. No constituye evidencia de resolucion del problema 3D de Navier-Stokes ni demostracion matematica.

## Lectura de estados en el JSON

- `execution_status`: indica si la corrida y el pipeline de validacion terminaron correctamente con metricas finitas.
- `accuracy_status`: indica el nivel de evaluacion de precision numerica.
- `status`: campo legacy, conservado por compatibilidad, alineado con `execution_status`.

Interpretacion prudente:

- `execution_status=passed` no implica aceptacion cientifica fuerte.
- `accuracy_status=warning` o `not_evaluated` exige revision humana antes de conclusiones.

## Riesgos de falso positivo

- Metricas finitas no implican precision suficiente.
- `status=passed` puede significar ejecucion correcta, no exactitud cientifica.
- Error por resolucion insuficiente.
- Error por paso temporal no refinado.
- Error por condiciones de frontera fuera del dominio de interes.
- Error por discretizacion aun con series finitas.
- Error por comparacion analitica en grilla/tiempo no equivalentes.
- Error por ausencia de tolerancias explicitas.

## Preguntas criticas

1. Que significa exactamente `passed` en este contexto?
2. Existen tolerancias numericas explicitas?
3. Los errores `L2` y `L∞` son aceptables para esta resolucion?
4. Se compara contra solucion exacta en `t=0` y `t>0`?
5. La energia decae de forma consistente con la tendencia analitica?
6. Se distingue ejecucion exitosa de precision aceptable?
7. El resultado es reproducible con igual configuracion?
8. El error mejora al aumentar resolucion?

## Recomendaciones siguientes

- Mantener separacion `execution_status` vs `accuracy_status`.
- Incorporar tolerancias configurables y trazables.
- Evaluar varias resoluciones con mismo horizonte fisico.
- Agregar chequeo explicito de decaimiento de energia.
- Reportar resolucion, `dt`, pasos y norma inicial/final.
- Mantener lista de `warnings` como salida obligatoria.
- Mantener disclaimer: este flujo no prueba existencia/suavidad 3D.

## Criterios minimos de aceptacion cientifica

- Metricas finitas.
- Tolerancias explicitas.
- Configuracion completa persistida en JSON.
- Reproducibilidad verificable.
- Comparacion contra baseline.
- Mejora esperada bajo refinamiento.
- Revision humana previa a conclusiones cientificas.

## Limites explicitos

- No es prueba matematica.
- No es validacion 3D.
- No descarta singularidades.
- No demuestra suavidad global.
- No reemplaza analisis teorico ni revision cientifica externa.
