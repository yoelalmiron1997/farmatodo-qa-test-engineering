---
id: TC-ALG-004
title: Orden por frecuencia y desempate alfabético
requirement_ids:
- REQ-ALG-006
priority: P0
test_type: functional
level: unit
automation: planned
risk: high
risk_assessment:
  impact: 5
  likelihood: 3
  score: 15
  computed_priority: P0
techniques:
- Tabla de decisión
mandatory_deliverable: false
external_dependencies:
- Ninguna externa
hypotheses: []
tags:
- algorithm
status: draft
spec_version: 1
---

# TC-ALG-004 — Orden por frecuencia y desempate alfabético

## Objetivo
Verificar el orden descendente por frecuencia y alfabético en empates.

## Justificación de la prioridad
Impacto 5 × Probabilidad 3 = **15** → regla: P0.

Requisito explícito del PDF con riesgo real de implementar el desempate al revés o por orden de aparición.

## Precondiciones
- Entorno Python del proyecto instalado; sin red (sockets deshabilitados en la suite unitaria).

## Datos de entrada
- `b a b a c` → a: 2, b: 2, c: 1
- `z y y x x x` → x: 3, y: 2, z: 1

## Pasos
1. Invocar el análisis.
2. Comparar la secuencia ordenada de (palabra, frecuencia).

## Resultado esperado
- Secuencias exactamente iguales a las esperadas.

## Criterio de aceptación
Orden == esperado.

## Evidencias esperadas
- Resultado JUnit/JSON de pytest
- Mensaje de aserción con entrada, esperado y actual

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-ALG-004")`; no se mantiene a mano.
