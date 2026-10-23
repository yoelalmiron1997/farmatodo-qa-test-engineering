---
id: TC-FW-008
title: Evaluación del quality gate
requirement_ids:
- REQ-QA-001
- REQ-QA-005
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
- framework
- flaky
status: draft
spec_version: 1
---

# TC-FW-008 — Evaluación del quality gate

## Objetivo
Verificar que la política configurada bloquea o advierte según prioridad y estado.

## Justificación de la prioridad
Impacto 5 × Probabilidad 3 = **15** → regla: P0.

Un gate defectuoso convierte fallos reales en jobs verdes: es el componente con mayor impacto de ocultamiento.

## Precondiciones
- Entorno Python del proyecto instalado; sin red (sockets deshabilitados en la suite unitaria).

## Datos de entrada
- P0 FAIL
- P0 FLAKY
- P0 BLOCKED
- P1 FAIL
- P1 FLAKY
- P2 FAIL
- P2 FLAKY
- Todo PASS

## Pasos
1. Evaluar cada escenario con la política por defecto.
2. Evaluar con una política alternativa (FLAKY P0 → warn).

## Resultado esperado
- Ver tabla del SDD Anexo C.5.

## Criterio de aceptación
Decisión del gate == tabla.

## Evidencias esperadas
- Resultado JUnit/JSON de pytest
- Mensaje de aserción con entrada, esperado y actual

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-FW-008")`; no se mantiene a mano.
