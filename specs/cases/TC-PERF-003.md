---
id: TC-PERF-003
title: Tiempo de actualización de Keyword Density
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
- H-03
tags:
- performance
status: draft
spec_version: 1
---

# TC-PERF-003 — Tiempo de actualización de Keyword Density

## Objetivo
Medir el intervalo entre cambiar el contenido y observar las tres frecuencias esperadas.

## Justificación de la prioridad
Impacto 2 × Probabilidad 2 = **4** → regla: P2.

P2. Keyword Density puede recalcularse con debounce; documentarlo evita esperas mal dimensionadas en E2E.

## Precondiciones
- Navegador Chrome headless con perfil temporal nuevo (sin localStorage ni cookies previos).
- Probe de disponibilidad de https://wordcounter.net/ exitoso; si falla, el caso se marca BLOCKED (ver SDD §5.6).
- Configuración por defecto del sitio, sin modificar opciones (REQ-WC-004).

## Datos de entrada
- Texto de TC-WC-003; n = 5 + 1 warm-up

## Pasos
1. Cargar un texto base.
2. t0; reemplazar por el texto objetivo.
3. Esperar top-3 == oráculo; t1.
4. Registrar ambas series.

## Resultado esperado
- Series registradas; posible debounce documentado como característica, no como defecto.

## Criterio de aceptación
Mediciones completas y etiquetadas.

## Evidencias esperadas
- JSON de muestras con contexto

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-PERF-003")`; no se mantiene a mano.
