---
id: TC-WC-016
title: Emojis y caracteres fuera del BMP
requirement_ids:
- REQ-WC-002
priority: P2
test_type: functional
level: e2e
automation: planned
risk: low
risk_assessment:
  impact: 2
  likelihood: 3
  score: 6
  computed_priority: P2
techniques:
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

# TC-WC-016 — Emojis y caracteres fuera del BMP

## Objetivo
Documentar si el contador de caracteres cuenta puntos de código o unidades UTF-16.

## Justificación de la prioridad
Impacto 2 × Probabilidad 3 = **6** → regla: P2.

Caso poco frecuente pero revelador: JavaScript cuenta un emoji como 2 unidades. ChromeDriver no tipea caracteres fuera del BMP con send_keys, por lo que se inyecta por JavaScript.

## Precondiciones
- Navegador Chrome headless con perfil temporal nuevo (sin localStorage ni cookies previos).
- Probe de disponibilidad de https://wordcounter.net/ exitoso; si falla, el caso se marca BLOCKED (ver SDD §5.6).
- Configuración por defecto del sitio, sin modificar opciones (REQ-WC-004).

## Datos de entrada
- `hola 👋 mundo 🌎`

## Pasos
1. Abrir un WebDriver nuevo (fixture de alcance function) y navegar a https://wordcounter.net/.
2. Esperar con Expected Conditions a que el editor sea interactuable.
3. Limpiar el editor.
4. Cargar el texto por JavaScript + evento `keyup`.
5. Leer palabras y caracteres.

## Resultado esperado
- Palabras = 4; caracteres = 16 (el sitio cuenta unidades UTF-16; ver BUG-WC-004).

## Criterio de aceptación
Valor visible == oráculo con perfil UTF-16 (caracterización del comportamiento actual).

## Evidencias esperadas
- Registro estructurado por intento (JSON normalizado)
- Ante fallo: screenshot PNG + HTML del DOM + mensaje esperado/actual
- Versión de navegador y driver en el resultado de la ejecución

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-WC-016")`; no se mantiene a mano.
