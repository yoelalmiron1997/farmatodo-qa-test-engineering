---
id: TC-FW-006
title: Validación del esquema de resultados
requirement_ids:
- REQ-QA-004
- REQ-QA-005
priority: P1
test_type: functional
level: unit
automation: planned
risk: medium
risk_assessment:
  impact: 4
  likelihood: 2
  score: 8
  computed_priority: P1
techniques:
- Partición de equivalencia
mandatory_deliverable: false
external_dependencies:
- Ninguna externa
hypotheses: []
tags:
- framework
- schema
status: draft
spec_version: 1
---

# TC-FW-006 — Validación del esquema de resultados

## Objetivo
Verificar que resultados válidos se aceptan y que versión, Case ID o campos faltantes se rechazan.

## Justificación de la prioridad
Impacto 4 × Probabilidad 2 = **8** → regla: P1.

El esquema es el contrato entre ejecución y portal.

## Precondiciones
- Entorno Python del proyecto instalado; sin red (sockets deshabilitados en la suite unitaria).

## Datos de entrada
- Resultado válido v1
- schema_version desconocida
- intento sin case_id
- timestamp inválido

## Pasos
1. Validar cada documento.

## Resultado esperado
- Solo el válido se acepta; cada rechazo indica la ruta del campo.

## Criterio de aceptación
Validación == esperada.

## Evidencias esperadas
- Resultado JUnit/JSON de pytest
- Mensaje de aserción con entrada, esperado y actual

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-FW-006")`; no se mantiene a mano.
