# Diagnosticos Fisicos Minimos (2D Incompresible)

## Objetivo
Definir el set minimo de observables para habilitar validacion fisica base de corridas 2D incompresibles, evitando respuestas `INSUFFICIENT DATA`.

## Definicion de energia cinetica total E(t)
Para campo de velocidad 2D `(u, v)`:

`E = 0.5 * integral(u^2 + v^2) dA`

En grilla uniforme:

`E = 0.5 * sum(u^2 + v^2) * dx * dy`

## Definicion de enstrofia total Omega(t)
Para vorticidad `omega`:

`Omega = 0.5 * integral(omega^2) dA`

En grilla uniforme:

`Omega = 0.5 * sum(omega^2) * dx * dy`

## Por que son necesarias
- `E(t)` permite detectar crecimiento no fisico en regimen viscoso y verificar conservacion aproximada en casos inviscidos controlados.
- `Omega(t)` es metrica critica en 2D para detectar cascadas no plausibles o inestabilidades numericas.
- Metadata fisica (viscosidad, resolucion, dt, condicion inicial, de-aliasing) es necesaria para interpretar los observables.

## Informacion minima por corrida
Cada corrida debe exponer al menos:
- `energy`
- `enstrophy`
- `viscosity`
- `resolution.nx`
- `resolution.ny`
- `dt`
- `t`
- `initial_condition`
- `dealiasing_method`

Si cualquiera de estos campos falta, la validacion fisica debe fallar en modo fail-closed.

## Limitacion explicita
Estos diagnosticos habilitan validacion fisica minima en una configuracion 2D controlada. No prueban resolucion del problema 3D de Navier-Stokes, no prueban existencia/suavidad global y no constituyen demostracion del Problema del Milenio.
