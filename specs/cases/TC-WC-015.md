---
id: TC-WC-015
title: Comportamiento por defecto de Keyword Density con stop words
requirement_ids:
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
- Caracterización
- Prueba de regresión del perfil del oráculo
mandatory_deliverable: false
external_dependencies:
- wordcounter.net (tercero, fuera de nuestro control)
- Google Chrome + driver resuelto por Selenium Manager
- Conexión a Internet
hypotheses: []
tags:
- wordcounter
status: draft
spec_version: 1
---

# TC-WC-015 — Comportamiento por defecto de Keyword Density con stop words

## Objetivo
Fijar como regresión cómo Keyword Density trata stop words y palabras cortas en la configuración por defecto.

## Justificación de la prioridad
Impacto 4 × Probabilidad 3 = **12** → regla: P1.

Es la base del oráculo de Keyword Density: si cambia la regla del sitio, TC-WC-003/004 pueden fallar por motivos distintos a un defecto. Detectarlo por separado acelera el diagnóstico.

## Precondiciones
- Navegador Chrome headless con perfil temporal nuevo (sin localStorage ni cookies previos).
- Probe de disponibilidad de https://wordcounter.net/ exitoso; si falla, el caso se marca BLOCKED (ver SDD §5.6).
- Configuración por defecto del sitio, sin modificar opciones (REQ-WC-004).

## Datos de entrada
- `the the the and and data data data data` → solo data 4
- `b c d` → sin entradas (palabras de una letra excluidas)
- `1,000 2.000` → sin entradas (números excluidos)

## Pasos
1. Abrir un WebDriver nuevo (fixture de alcance function) y navegar a https://wordcounter.net/.
2. Esperar con Expected Conditions a que el editor sea interactuable.
3. Limpiar el editor.
4. Ingresar el texto.
5. Leer todas las entradas visibles de Keyword Density.

## Resultado esperado
- Las entradas visibles coinciden exactamente con el perfil del oráculo.

## Criterio de aceptación
Entradas visibles == oráculo.

## Evidencias esperadas
- Registro estructurado por intento (JSON normalizado)
- Ante fallo: screenshot PNG + HTML del DOM + mensaje esperado/actual
- Versión de navegador y driver en el resultado de la ejecución

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-WC-015")`; no se mantiene a mano.
