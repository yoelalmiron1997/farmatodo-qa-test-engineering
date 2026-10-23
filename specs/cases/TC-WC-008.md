---
id: TC-WC-008
title: Actualización del contenido
requirement_ids:
- REQ-WC-001
- REQ-WC-002
- REQ-WC-003
priority: P1
test_type: functional
level: e2e
automation: planned
risk: medium
risk_assessment:
  impact: 4
  likelihood: 3
  score: 12
  computed_priority: P1
techniques:
- Transición de estados
mandatory_deliverable: false
external_dependencies:
- wordcounter.net (tercero, fuera de nuestro control)
- Google Chrome + driver resuelto por Selenium Manager
- Conexión a Internet
hypotheses: []
tags:
- wordcounter
- regression
status: draft
spec_version: 1
---

# TC-WC-008 — Actualización del contenido

## Objetivo
Verificar que al reemplazar o ampliar el texto los tres indicadores reflejan solo el contenido actual.

## Justificación de la prioridad
Impacto 4 × Probabilidad 3 = **12** → regla: P1.

La UI se recalcula en eventos del editor: riesgo de valores obsoletos y fuente típica de flakiness por sincronización.

## Precondiciones
- Navegador Chrome headless con perfil temporal nuevo (sin localStorage ni cookies previos).
- Probe de disponibilidad de https://wordcounter.net/ exitoso; si falla, el caso se marca BLOCKED (ver SDD §5.6).
- Configuración por defecto del sitio, sin modificar opciones (REQ-WC-004).

## Datos de entrada
- Texto A: `uno dos tres` → 3 palabras
- Texto B (reemplazo): `alfa alfa beta` → 3 palabras; alfa 2
- Texto C (agregado a B): ` gamma` → 4 palabras

## Pasos
1. Abrir un WebDriver nuevo (fixture de alcance function) y navegar a https://wordcounter.net/.
2. Esperar con Expected Conditions a que el editor sea interactuable.
3. Limpiar el editor.
4. Ingresar A y esperar contadores estables.
5. Seleccionar todo, borrar e ingresar B.
6. Verificar contadores y Keyword Density de B.
7. Agregar C al final y verificar.

## Resultado esperado
- Tras cada transición, los indicadores corresponden exclusivamente al texto vigente.

## Criterio de aceptación
Cada estado intermedio == oráculo; ningún valor de A persiste.

## Evidencias esperadas
- Registro estructurado por intento (JSON normalizado)
- Ante fallo: screenshot PNG + HTML del DOM + mensaje esperado/actual
- Versión de navegador y driver en el resultado de la ejecución

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-WC-008")`; no se mantiene a mano.
