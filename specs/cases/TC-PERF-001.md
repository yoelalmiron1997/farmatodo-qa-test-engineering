---
id: TC-PERF-001
title: Tiempo de navegación de WordCounter
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
- Medición con Navigation Timing API
mandatory_deliverable: false
external_dependencies:
- wordcounter.net (tercero, fuera de nuestro control)
- Google Chrome + driver resuelto por Selenium Manager
- Conexión a Internet
hypotheses: []
tags:
- performance
status: draft
spec_version: 1
---

# TC-PERF-001 — Tiempo de navegación de WordCounter

## Objetivo
Medir el tiempo de carga inicial con Navigation Timing (TTFB, DOMContentLoaded, load) y la disponibilidad del editor.

## Justificación de la prioridad
Impacto 2 × Probabilidad 2 = **4** → regla: P2.

P2 por definición de la consigna: aporta línea base y contexto, no es objetivo del PDF.

## Precondiciones
- Navegador Chrome headless con perfil temporal nuevo (sin localStorage ni cookies previos).
- Probe de disponibilidad de https://wordcounter.net/ exitoso; si falla, el caso se marca BLOCKED (ver SDD §5.6).
- Configuración por defecto del sitio, sin modificar opciones (REQ-WC-004).
- Workflow de performance (manual o semanal); nunca en PR.

## Datos de entrada
- n = 5 muestras + 1 warm-up descartado, secuenciales, perfil nuevo por muestra

## Pasos
1. Abrir navegador nuevo.
2. Navegar a la URL.
3. Leer `performance.getEntriesByType('navigation')[0]`.
4. Registrar responseStart, domContentLoadedEventEnd, loadEventEnd y el tiempo hasta editor interactuable.
5. Cerrar navegador; repetir.

## Resultado esperado
- Muestras registradas con entorno; estadística descriptiva; sin umbral hasta tener baseline.

## Criterio de aceptación
Mediciones válidas y completas; el caso falla solo si la medición no pudo tomarse (no por lentitud) hasta que exista un umbral aprobado.

## Evidencias esperadas
- JSON de muestras con contexto (runner, región, versión de Chrome)

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-PERF-001")`; no se mantiene a mano.
