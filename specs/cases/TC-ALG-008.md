---
id: TC-ALG-008
title: 'Unicode: acentos, ñ y normalización'
requirement_ids:
- REQ-ALG-002
- REQ-ALG-006
priority: P1
test_type: functional
level: unit
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
- Ninguna externa
hypotheses: []
tags:
- algorithm
- i18n
status: draft
spec_version: 1
---

# TC-ALG-008 — Unicode: acentos, ñ y normalización

## Objetivo
Verificar que palabras con tildes no se fragmentan y que formas compuestas y descompuestas se unifican (NFC).

## Justificación de la prioridad
Impacto 4 × Probabilidad 3 = **12** → regla: P1.

Texto en español; un tokenizador ASCII es un defecto probable.

## Precondiciones
- Entorno Python del proyecto instalado; sin red (sockets deshabilitados en la suite unitaria).

## Datos de entrada
- `Niño niño ÁRBOL árbol` → niño: 2, árbol: 2
- `camión` (NFC) y `camio\u0301n` (NFD) → camión: 2

## Pasos
1. Invocar el análisis.

## Resultado esperado
- Frecuencias unificadas; orden de empate determinista según D-ALG-2.

## Criterio de aceptación
Valores y orden == esperados.

## Evidencias esperadas
- Resultado JUnit/JSON de pytest
- Mensaje de aserción con entrada, esperado y actual

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-ALG-008")`; no se mantiene a mano.
