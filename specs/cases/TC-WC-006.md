---
id: TC-WC-006
title: Signos de puntuación
requirement_ids:
- REQ-WC-001
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
- Partición de equivalencia
- Caracterización
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

# TC-WC-006 — Signos de puntuación

## Objetivo
Verificar que la puntuación adyacente no altera el conteo de palabras ni separa entradas en Keyword Density.

## Justificación de la prioridad
Impacto 4 × Probabilidad 3 = **12** → regla: P1.

Los textos reales contienen puntuación; un sitio que agrupe `hola` y `hola,` por separado reportaría un top-3 incorrecto.

## Precondiciones
- Navegador Chrome headless con perfil temporal nuevo (sin localStorage ni cookies previos).
- Probe de disponibilidad de https://wordcounter.net/ exitoso; si falla, el caso se marca BLOCKED (ver SDD §5.6).
- Configuración por defecto del sitio, sin modificar opciones (REQ-WC-004).

## Datos de entrada
- `Hola, mundo. Hola; mundo! (hola)` → 5 palabras; Keyword Density: hola 3, mundo 2
- `hola - mundo` → 2 palabras (el guion aislado no cuenta como palabra)

## Pasos
1. Abrir un WebDriver nuevo (fixture de alcance function) y navegar a https://wordcounter.net/.
2. Esperar con Expected Conditions a que el editor sea interactuable.
3. Limpiar el editor.
4. Ingresar el texto.
5. Leer palabras y Keyword Density.
6. Comparar con el oráculo.

## Resultado esperado
- Palabras = 5 y 2.
- Keyword Density agrupa `hola` (3) y `mundo` (2) sin puntuación.

## Criterio de aceptación
Valores visibles == oráculo.

## Evidencias esperadas
- Registro estructurado por intento (JSON normalizado)
- Ante fallo: screenshot PNG + HTML del DOM + mensaje esperado/actual
- Versión de navegador y driver en el resultado de la ejecución

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-WC-006")`; no se mantiene a mano.
