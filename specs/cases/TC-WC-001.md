---
id: TC-WC-001
title: Conteo básico de palabras
requirement_ids:
- REQ-WC-001
priority: P0
test_type: functional
level: e2e
automation: planned
risk: high
risk_assessment:
  impact: 5
  likelihood: 3
  score: 15
  computed_priority: P0
techniques:
- Partición de equivalencia
mandatory_deliverable: false
external_dependencies:
- wordcounter.net (tercero, fuera de nuestro control)
- Google Chrome + driver resuelto por Selenium Manager
- Conexión a Internet
hypotheses: []
tags:
- wordcounter
- smoke
status: draft
spec_version: 1
---

# TC-WC-001 — Conteo básico de palabras

## Objetivo
Verificar que el contador de palabras refleja el número de palabras de textos simples y sin ambigüedad.

## Justificación de la prioridad
Impacto 5 × Probabilidad 3 = **15** → regla: P0.

Objetivo central del Ejercicio 1. Datos ASCII sin puntuación para que la regla de separación no admita interpretaciones: un fallo aquí es un defecto, no una diferencia de criterio.

## Precondiciones
- Navegador Chrome headless con perfil temporal nuevo (sin localStorage ni cookies previos).
- Probe de disponibilidad de https://wordcounter.net/ exitoso; si falla, el caso se marca BLOCKED (ver SDD §5.6).
- Configuración por defecto del sitio, sin modificar opciones (REQ-WC-004).

## Datos de entrada
- `the quick brown fox jumps over the lazy dog` → 9
- `farmatodo cuida tu salud todos los dias` → 7
- `salud` → 1

## Pasos
1. Abrir un WebDriver nuevo (fixture de alcance function) y navegar a https://wordcounter.net/.
2. Esperar con Expected Conditions a que el editor sea interactuable.
3. Limpiar el editor.
4. Ingresar el texto parametrizado.
5. Esperar a que el contador de palabras muestre un valor estable.
6. Leer el contador de palabras.
7. Comparar con el valor calculado por el oráculo a partir del texto de entrada.

## Resultado esperado
- El contador de palabras muestra 9, 7 y 1 respectivamente.

## Criterio de aceptación
Para cada dato parametrizado, valor visible == valor del oráculo; la aserción informa texto, esperado y actual.

## Evidencias esperadas
- Registro estructurado por intento (JSON normalizado)
- Ante fallo: screenshot PNG + HTML del DOM + mensaje esperado/actual
- Versión de navegador y driver en el resultado de la ejecución

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-WC-001")`; no se mantiene a mano.
