# Definición de indicadores

Los estados son por **caso**; los intentos y reintentos, por **ejecución de test** (un caso parametrizado tiene varias ejecuciones). El estado de un caso es el más severo de sus ejecuciones: FAIL > FLAKY > BLOCKED > NOT RUN > PASS > SKIPPED.

## Estados

| Estado | Definición |
|---|---|
| PASS limpio | Pasó en el primer intento. |
| FLAKY observado | Falló al menos una vez y pasó en un intento posterior **de la misma corrida**. Nunca se cuenta como PASS. |
| FAIL | El último intento permitido falló (incluye timeouts que terminan fallando). |
| SKIPPED | Omitido deliberadamente. |
| BLOCKED | Falló una precondición externa verificada **antes** del cuerpo del test. |
| NOT RUN | Especificado y dentro del alcance de la corrida, pero sin ejecución. |
| Flaky sospechado | En corridas comparables (misma especificación, entorno y versión mayor del navegador) alterna PASS/FAIL: n ≥ 5 y (flip rate ≥ 0,2 o ≥ 2 FLAKY), sin estar fallando de forma consistente en las últimas 3. |

## Fórmulas

| Indicador | Fórmula |
|---|---|
| Ejecutados (E) | casos con estado PASS, FLAKY o FAIL |
| Aprobación al primer intento | PASS / E |
| Aprobación final | (PASS + FLAKY) / E — siempre junto a la anterior |
| % flaky observado | FLAKY / E |
| Intentos | Σ intentos de las ejecuciones de casos ejecutados |
| Reintentos | Σ (intentos − 1) por ejecución |
| Casos con reintentos | casos con alguna ejecución de más de un intento |
| Tiempo medio por caso | Σ duración de todos los intentos / E (incluye el costo de los reintentos) |
| Estabilidad de un caso | PASS limpios / n en la ventana de las últimas 20 corridas comparables |
| Flip rate | cambios de estado entre corridas consecutivas / (n − 1) |
| Top 10 inestables | orden por (1 − estabilidad), luego flip rate y luego n; solo n ≥ 3 |
| Fallos por categoría | intentos fallidos de la categoría / intentos fallidos totales |
| Cobertura de requisitos especificada | requisitos con ≥ 1 caso o verificación no-test declarada / requisitos (separado PDF y derivados) |
| Cobertura de requisitos ejecutada | requisitos `test` con ≥ 1 caso ejecutado en la última corrida / requisitos `test` |
| Cobertura de automatización | casos con test vinculado por marker / casos automatizables, por prioridad |
| Defectos confirmados | reportes con `status: confirmed` |
| Evidencias disponibles | intentos fallidos con captura y DOM / intentos fallidos |

!!! warning "Tres cosas distintas"
    **Cobertura de requisitos** (qué requisitos tienen pruebas), **cobertura de código** (qué líneas del framework ejecutan los tests; coverage.py en `pr-checks`) y **tasa de aprobación** (qué proporción pasó) no son intercambiables.

## Performance
n, mínimo, media, mediana y máximo siempre; desvío estándar solo si n ≥ 3; P95 solo si n ≥ 20. Baseline = mediana de las medianas de las primeras 5 corridas válidas del mismo entorno. Una **alerta** requiere a la vez +50 % y +200 ms sobre el baseline. Es un cambio significativo según una regla documentada, no una prueba estadística de regresión.
