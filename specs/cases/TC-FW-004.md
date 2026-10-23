---
id: TC-FW-004
title: Validador de especificaciones y trazabilidad
requirement_ids:
- REQ-QA-003
- REQ-QA-005
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
- Tabla de decisión
- Adivinación de errores
mandatory_deliverable: false
external_dependencies:
- Ninguna externa
hypotheses: []
tags:
- framework
- traceability
status: draft
spec_version: 1
---

# TC-FW-004 — Validador de especificaciones y trazabilidad

## Objetivo
Verificar que el validador detecta cada inconsistencia definida en el SDD §10.3.

## Justificación de la prioridad
Impacto 4 × Probabilidad 3 = **12** → regla: P1.

Garantiza que el SDD y el catálogo no diverjan silenciosamente.

## Precondiciones
- Entorno Python del proyecto instalado; sin red (sockets deshabilitados en la suite unitaria).

## Datos de entrada
- Fixtures de specs con: ID duplicado, caso huérfano, prioridad desconocida, campo faltante, caso automatizado sin test, test sin Case ID, requisito sin casos, prioridad inconsistente con el riesgo sin override

## Pasos
1. Ejecutar el validador sobre cada fixture.

## Resultado esperado
- Un error específico y localizable por cada inconsistencia; specs válidas → sin errores.

## Criterio de aceptación
Errores reportados == inconsistencias sembradas.

## Evidencias esperadas
- Resultado JUnit/JSON de pytest
- Mensaje de aserción con entrada, esperado y actual

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-FW-004")`; no se mantiene a mano.
