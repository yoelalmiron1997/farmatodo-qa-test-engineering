---
id: TC-ALG-002
title: Conteo de palabras
requirement_ids:
- REQ-ALG-003
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
- Partición de equivalencia
- Valores límite
mandatory_deliverable: false
external_dependencies:
- Ninguna externa
hypotheses: []
tags:
- algorithm
status: draft
spec_version: 1
---

# TC-ALG-002 — Conteo de palabras

## Objetivo
Verificar el conteo de palabras para separadores múltiples y entradas vacías.

## Justificación de la prioridad
Impacto 5 × Probabilidad 3 = **15** → regla: P0.

Comportamiento indispensable del algoritmo propio.

## Precondiciones
- Entorno Python del proyecto instalado; sin red (sockets deshabilitados en la suite unitaria).

## Datos de entrada
- `a b  c` → 3
- `` → 0
- `\n\n` → 0
- `uno\ndos` → 2

## Pasos
1. Invocar la función de análisis con cada texto.
2. Comparar el total de palabras.

## Resultado esperado
- 3, 0, 0 y 2 respectivamente.

## Criterio de aceptación
Total == esperado para cada partición.

## Evidencias esperadas
- Resultado JUnit/JSON de pytest
- Mensaje de aserción con entrada, esperado y actual

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-ALG-002")`; no se mantiene a mano.
