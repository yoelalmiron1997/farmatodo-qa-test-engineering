---
id: TC-ALG-007
title: Puntuación y mayúsculas
requirement_ids:
- REQ-ALG-002
- REQ-ALG-003
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
status: draft
spec_version: 1
---

# TC-ALG-007 — Puntuación y mayúsculas

## Objetivo
Verificar que la puntuación no forma parte de la palabra y que la frecuencia ignora mayúsculas.

## Justificación de la prioridad
Impacto 4 × Probabilidad 3 = **12** → regla: P1.

Decisión de diseño D-ALG-1 no explícita en el PDF; debe quedar fijada por prueba.

## Precondiciones
- Entorno Python del proyecto instalado; sin red (sockets deshabilitados en la suite unitaria).

## Datos de entrada
- `Hola, hola. HOLA!` → 3 palabras, 17 caracteres, hola: 3

## Pasos
1. Invocar el análisis.

## Resultado esperado
- 3 palabras, 17 caracteres, una sola entrada `hola: 3`.

## Criterio de aceptación
Valores == esperados.

## Evidencias esperadas
- Resultado JUnit/JSON de pytest
- Mensaje de aserción con entrada, esperado y actual

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-ALG-007")`; no se mantiene a mano.
