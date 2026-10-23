---
id: TC-WC-014
title: Texto extenso
requirement_ids:
- REQ-WC-001
- REQ-WC-002
- REQ-WC-003
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
- Prueba de volumen ligera
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

# TC-WC-014 — Texto extenso

## Objetivo
Verificar la exactitud de los contadores con un texto de ~2.000 palabras generado de forma determinista.

## Justificación de la prioridad
Impacto 3 × Probabilidad 2 = **6** → regla: P2.

Detecta truncamientos o desbordes; costo alto de ejecución con send_keys, por eso P2.

## Precondiciones
- Navegador Chrome headless con perfil temporal nuevo (sin localStorage ni cookies previos).
- Probe de disponibilidad de https://wordcounter.net/ exitoso; si falla, el caso se marca BLOCKED (ver SDD §5.6).
- Configuración por defecto del sitio, sin modificar opciones (REQ-WC-004).

## Datos de entrada
- Texto generado con semilla fija (2.000 palabras de un vocabulario de 50 palabras ASCII)

## Pasos
1. Abrir un WebDriver nuevo (fixture de alcance function) y navegar a https://wordcounter.net/.
2. Esperar con Expected Conditions a que el editor sea interactuable.
3. Limpiar el editor.
4. Cargar el texto en el editor (asignación por JavaScript + evento `keyup`, que es el que dispara el recálculo; justificado por costo).
5. Leer contadores y Keyword Density.
6. Comparar con el oráculo.

## Resultado esperado
- Contadores y top-3 == oráculo.

## Criterio de aceptación
Valores visibles == oráculo.

## Evidencias esperadas
- Registro estructurado por intento (JSON normalizado)
- Ante fallo: screenshot PNG + HTML del DOM + mensaje esperado/actual
- Versión de navegador y driver en el resultado de la ejecución

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-WC-014")`; no se mantiene a mano.
