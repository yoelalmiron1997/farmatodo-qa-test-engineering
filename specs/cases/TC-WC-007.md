---
id: TC-WC-007
title: Mayúsculas y minúsculas en Keyword Density
requirement_ids:
- REQ-WC-003
priority: P1
test_type: functional
level: e2e
automation: planned
risk: medium
risk_assessment:
  impact: 3
  likelihood: 3
  score: 9
  computed_priority: P1
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
status: draft
spec_version: 1
---

# TC-WC-007 — Mayúsculas y minúsculas en Keyword Density

## Objetivo
Verificar que variantes de capitalización se agrupan como la misma palabra.

## Justificación de la prioridad
Impacto 3 × Probabilidad 3 = **9** → regla: P1.

Riesgo medio: si el sitio distingue mayúsculas, el top-3 cambia completamente con textos reales.

## Precondiciones
- Navegador Chrome headless con perfil temporal nuevo (sin localStorage ni cookies previos).
- Probe de disponibilidad de https://wordcounter.net/ exitoso; si falla, el caso se marca BLOCKED (ver SDD §5.6).
- Configuración por defecto del sitio, sin modificar opciones (REQ-WC-004).

## Datos de entrada
- `Salud salud SALUD bienestar Bienestar vida` → 6 palabras; salud 3, bienestar 2, vida 1

## Pasos
1. Abrir un WebDriver nuevo (fixture de alcance function) y navegar a https://wordcounter.net/.
2. Esperar con Expected Conditions a que el editor sea interactuable.
3. Limpiar el editor.
4. Ingresar el texto.
5. Leer Keyword Density.
6. Comparar con el oráculo.

## Resultado esperado
- Top-3: salud 3, bienestar 2, vida 1 (agrupación insensible a mayúsculas, confirmada).

## Criterio de aceptación
Valores visibles == oráculo.

## Evidencias esperadas
- Registro estructurado por intento (JSON normalizado)
- Ante fallo: screenshot PNG + HTML del DOM + mensaje esperado/actual
- Versión de navegador y driver en el resultado de la ejecución

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-WC-007")`; no se mantiene a mano.
