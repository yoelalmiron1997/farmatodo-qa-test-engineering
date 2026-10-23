---
id: TC-ALG-011
title: Separadores de espacio en blanco
requirement_ids:
- REQ-ALG-003
priority: P1
test_type: functional
level: unit
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
- Ninguna externa
hypotheses: []
tags:
- algorithm
status: draft
spec_version: 1
---

# TC-ALG-011 — Separadores de espacio en blanco

## Objetivo
Verificar tabulaciones, espacios múltiples y espacio no separable como separadores de palabras.

## Justificación de la prioridad
Impacto 3 × Probabilidad 3 = **9** → regla: P1.

Textos copiados de la web incluyen NBSP y tabulaciones.

## Precondiciones
- Entorno Python del proyecto instalado; sin red (sockets deshabilitados en la suite unitaria).

## Datos de entrada
- `uno\tdos` → 2
- `uno\u00a0dos` → 2
- `uno     dos` → 2

## Pasos
1. Invocar el análisis.

## Resultado esperado
- 2 palabras en cada caso.

## Criterio de aceptación
Valores == esperados.

## Evidencias esperadas
- Resultado JUnit/JSON de pytest
- Mensaje de aserción con entrada, esperado y actual

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-ALG-011")`; no se mantiene a mano.
