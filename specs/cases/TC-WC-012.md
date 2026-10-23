---
id: TC-WC-012
title: Acentos y ñ (texto en español)
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
- Partición de equivalencia
mandatory_deliverable: false
external_dependencies:
- wordcounter.net (tercero, fuera de nuestro control)
- Google Chrome + driver resuelto por Selenium Manager
- Conexión a Internet
hypotheses: []
tags:
- wordcounter
- i18n
status: draft
spec_version: 1
---

# TC-WC-012 — Acentos y ñ (texto en español)

## Objetivo
Verificar que palabras con tildes y ñ no se fragmentan ni se cuentan mal.

## Justificación de la prioridad
Impacto 4 × Probabilidad 3 = **12** → regla: P1.

El negocio de Farmatodo opera en español: una tokenización ASCII partiría `camión` en `cami` + `n`.

## Precondiciones
- Navegador Chrome headless con perfil temporal nuevo (sin localStorage ni cookies previos).
- Probe de disponibilidad de https://wordcounter.net/ exitoso; si falla, el caso se marca BLOCKED (ver SDD §5.6).
- Configuración por defecto del sitio, sin modificar opciones (REQ-WC-004).

## Datos de entrada
- `niño niño camión camión camión acción` → 6 palabras, 37 caracteres; camión 3, niño 2, acción 1

## Pasos
1. Abrir un WebDriver nuevo (fixture de alcance function) y navegar a https://wordcounter.net/.
2. Esperar con Expected Conditions a que el editor sea interactuable.
3. Limpiar el editor.
4. Ingresar el texto.
5. Leer contadores y Keyword Density.
6. Comparar con el oráculo.

## Resultado esperado
- Palabras = 6; caracteres = 37; top-3: camión 3, niño 2, acción 1.

## Criterio de aceptación
Valores visibles == oráculo.

## Evidencias esperadas
- Registro estructurado por intento (JSON normalizado)
- Ante fallo: screenshot PNG + HTML del DOM + mensaje esperado/actual
- Versión de navegador y driver en el resultado de la ejecución

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-WC-012")`; no se mantiene a mano.
