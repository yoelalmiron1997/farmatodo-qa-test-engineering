---
id: TC-WC-010
title: Texto multilínea
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
- Caracterización
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

# TC-WC-010 — Texto multilínea

## Objetivo
Verificar el conteo con saltos de línea y documentar si el sitio cuenta el salto como carácter.

## Justificación de la prioridad
Impacto 4 × Probabilidad 3 = **12** → regla: P1.

Los textos pegados suelen ser multilínea; la regla de saltos de línea es la principal diferencia potencial con el Ejercicio 4.

## Precondiciones
- Navegador Chrome headless con perfil temporal nuevo (sin localStorage ni cookies previos).
- Probe de disponibilidad de https://wordcounter.net/ exitoso; si falla, el caso se marca BLOCKED (ver SDD §5.6).
- Configuración por defecto del sitio, sin modificar opciones (REQ-WC-004).

## Datos de entrada
- `linea uno\nlinea dos\nlinea tres` → 6 palabras; 28 caracteres (sin saltos); linea 3

## Pasos
1. Abrir un WebDriver nuevo (fixture de alcance function) y navegar a https://wordcounter.net/.
2. Esperar con Expected Conditions a que el editor sea interactuable.
3. Limpiar el editor.
4. Ingresar el texto con saltos de línea reales (Shift+Enter no requerido en textarea).
5. Leer contadores y Keyword Density.
6. Comparar con el oráculo.

## Resultado esperado
- Palabras = 6; caracteres = 28; Keyword Density: linea 3 en primera posición.

## Criterio de aceptación
Valores visibles == oráculo.

## Evidencias esperadas
- Registro estructurado por intento (JSON normalizado)
- Ante fallo: screenshot PNG + HTML del DOM + mensaje esperado/actual
- Versión de navegador y driver en el resultado de la ejecución

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-WC-010")`; no se mantiene a mano.
