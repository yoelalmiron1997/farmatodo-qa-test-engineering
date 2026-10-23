---
id: TC-WC-013
title: Números, guiones y apóstrofes
requirement_ids:
- REQ-WC-001
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

# TC-WC-013 — Números, guiones y apóstrofes

## Objetivo
Documentar cómo se cuentan tokens con números, guiones internos y apóstrofes.

## Justificación de la prioridad
Impacto 2 × Probabilidad 3 = **6** → regla: P2.

Poco frecuente en el uso objetivo; sirve para documentar la regla real del sitio.

## Precondiciones
- Navegador Chrome headless con perfil temporal nuevo (sin localStorage ni cookies previos).
- Probe de disponibilidad de https://wordcounter.net/ exitoso; si falla, el caso se marca BLOCKED (ver SDD §5.6).
- Configuración por defecto del sitio, sin modificar opciones (REQ-WC-004).

## Datos de entrada
- `e-commerce 2026 don't 3.5 x-ray`

## Pasos
1. Abrir un WebDriver nuevo (fixture de alcance function) y navegar a https://wordcounter.net/.
2. Esperar con Expected Conditions a que el editor sea interactuable.
3. Limpiar el editor.
4. Ingresar el texto.
5. Leer el contador de palabras.

## Resultado esperado
- Palabras = 5.

## Criterio de aceptación
Valor visible == oráculo.

## Evidencias esperadas
- Registro estructurado por intento (JSON normalizado)
- Ante fallo: screenshot PNG + HTML del DOM + mensaje esperado/actual
- Versión de navegador y driver en el resultado de la ejecución

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-WC-013")`; no se mantiene a mano.
