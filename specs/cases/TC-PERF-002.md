---
id: TC-PERF-002
title: Tiempo de respuesta del contador
requirement_ids:
- REQ-QA-002
priority: P2
test_type: performance
level: e2e
automation: planned
risk: low
risk_assessment:
  impact: 2
  likelihood: 2
  score: 4
  computed_priority: P2
techniques:
- 'Medición dual: perf_counter + MutationObserver'
mandatory_deliverable: false
external_dependencies:
- wordcounter.net (tercero, fuera de nuestro control)
- Google Chrome + driver resuelto por Selenium Manager
- Conexión a Internet
hypotheses:
- H-04
tags:
- performance
status: draft
spec_version: 1
---

# TC-PERF-002 — Tiempo de respuesta del contador

## Objetivo
Medir el intervalo entre introducir el texto y observar el contador actualizado al valor esperado.

## Justificación de la prioridad
Impacto 2 × Probabilidad 2 = **4** → regla: P2.

P2. Diferencia explícitamente el tiempo extremo a extremo (incluye overhead de WebDriver) del tiempo dentro del navegador.

## Precondiciones
- Navegador Chrome headless con perfil temporal nuevo (sin localStorage ni cookies previos).
- Probe de disponibilidad de https://wordcounter.net/ exitoso; si falla, el caso se marca BLOCKED (ver SDD §5.6).
- Configuración por defecto del sitio, sin modificar opciones (REQ-WC-004).

## Datos de entrada
- Texto fijo de 50 palabras; n = 5 + 1 warm-up

## Pasos
1. Instalar un MutationObserver sobre el contador antes de la acción.
2. t0 = perf_counter(); disparar la entrada (asignación + evento `input`).
3. Esperar hasta que el contador == oráculo (sondeo de 25 ms); t1 = perf_counter().
4. Leer el delta medido en el navegador (performance.now()).
5. Registrar ambos valores y la resolución del sondeo.

## Resultado esperado
- Dos series: extremo a extremo (Python) e interna (navegador), etiquetadas por separado.

## Criterio de aceptación
Mediciones completas; la validación funcional (valor == oráculo) se registra aparte de la duración.

## Evidencias esperadas
- JSON de muestras con contexto

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-PERF-002")`; no se mantiene a mano.
