---
id: TC-WC-018
title: 'Reproducción BUG-WC-002: palabra formada solo por guiones'
requirement_ids:
- REQ-WC-001
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
known_defect: BUG-WC-002
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

# TC-WC-018 — Reproducción BUG-WC-002: palabra formada solo por guiones

## Objetivo
Verificar que un token sin letras ni dígitos no aparezca como palabra clave cuando el contador indica 0 palabras.

## Justificación de la prioridad
Impacto 3 × Probabilidad 2 = **6** → regla: P2.

Defecto confirmado en el Ejercicio 2; mismo criterio que TC-WC-017.

## Precondiciones
- Navegador Chrome headless con perfil temporal nuevo (sin localStorage ni cookies previos).
- Probe de disponibilidad de https://wordcounter.net/ exitoso; si falla, el caso se marca BLOCKED (ver SDD §5.6).
- Configuración por defecto del sitio, sin modificar opciones (REQ-WC-004).

## Datos de entrada
- `---`

## Pasos
1. Abrir un WebDriver nuevo (fixture de alcance function) y navegar a https://wordcounter.net/.
2. Esperar con Expected Conditions a que el editor sea interactuable.
3. Limpiar el editor.
4. Ingresar el texto.
5. Leer contador de palabras y Keyword Density.

## Resultado esperado
- Palabras = 0 y Keyword Density sin entradas.

## Criterio de aceptación
Coherencia entre contador y Keyword Density.

## Evidencias esperadas
- Registro estructurado por intento (JSON normalizado)
- Ante fallo: screenshot PNG + HTML del DOM + mensaje esperado/actual
- Versión de navegador y driver en el resultado de la ejecución

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-WC-018")`; no se mantiene a mano.
