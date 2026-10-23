---
id: TC-WC-019
title: 'Reproducción BUG-WC-003: espacio no separable'
requirement_ids:
- REQ-WC-003
- REQ-BUG-001
priority: P2
test_type: functional
level: e2e
automation: planned
risk: low
risk_assessment:
  impact: 3
  likelihood: 2
  score: 6
  computed_priority: P2
techniques:
- Prueba de defecto confirmado
mandatory_deliverable: false
known_defect: BUG-WC-003
external_dependencies:
- wordcounter.net (tercero, fuera de nuestro control)
- Google Chrome + driver resuelto por Selenium Manager
- Conexión a Internet
hypotheses: []
tags:
- wordcounter
- known-defect
status: draft
spec_version: 1
---

# TC-WC-019 — Reproducción BUG-WC-003: espacio no separable

## Objetivo
Verificar que Keyword Density separe palabras unidas por un espacio no separable (U+00A0), como ya hace el contador.

## Justificación de la prioridad
Impacto 3 × Probabilidad 2 = **6** → regla: P2.

Defecto confirmado en el Ejercicio 2. El NBSP es habitual al copiar texto desde páginas web y procesadores de texto.

## Precondiciones
- Navegador Chrome headless con perfil temporal nuevo (sin localStorage ni cookies previos).
- Probe de disponibilidad de https://wordcounter.net/ exitoso; si falla, el caso se marca BLOCKED (ver SDD §5.6).
- Configuración por defecto del sitio, sin modificar opciones (REQ-WC-004).

## Datos de entrada
- `uno dos` (cargado por JavaScript + `keyup`)

## Pasos
1. Abrir un WebDriver nuevo (fixture de alcance function) y navegar a https://wordcounter.net/.
2. Esperar con Expected Conditions a que el editor sea interactuable.
3. Limpiar el editor.
4. Cargar el texto.
5. Leer contador y Keyword Density.

## Resultado esperado
- Palabras = 2 y Keyword Density con `uno` 1 y `dos` 1.

## Criterio de aceptación
Keyword Density == oráculo.

## Evidencias esperadas
- Registro estructurado por intento (JSON normalizado)
- Ante fallo: screenshot PNG + HTML del DOM + mensaje esperado/actual
- Versión de navegador y driver en el resultado de la ejecución

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-WC-019")`; no se mantiene a mano.
