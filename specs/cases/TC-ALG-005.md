---
id: TC-ALG-005
title: Archivo vacío
requirement_ids:
- REQ-ALG-001
- REQ-ALG-003
- REQ-ALG-004
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

# TC-ALG-005 — Archivo vacío

## Objetivo
Verificar que un archivo vacío produce totales en cero sin errores.

## Justificación de la prioridad
Impacto 3 × Probabilidad 3 = **9** → regla: P1.

Valor límite inferior común en entradas reales.

## Precondiciones
- Entorno Python del proyecto instalado; sin red (sockets deshabilitados en la suite unitaria).

## Datos de entrada
- Archivo vacío
- Archivo con solo saltos de línea

## Pasos
1. Ejecutar la CLI con cada archivo.

## Resultado esperado
- `0 words` y `0 characters`, sin líneas de frecuencia; código de salida 0.

## Criterio de aceptación
Salida y código == esperados.

## Evidencias esperadas
- Resultado JUnit/JSON de pytest
- Mensaje de aserción con entrada, esperado y actual

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-ALG-005")`; no se mantiene a mano.
