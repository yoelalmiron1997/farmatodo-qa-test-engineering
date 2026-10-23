---
id: TC-FW-001
title: Clasificación de intentos y flaky observado
requirement_ids:
- REQ-QA-001
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

# TC-FW-001 — Clasificación de intentos y flaky observado

## Objetivo
Verificar que las secuencias de intentos se clasifican en el estado final correcto.

## Justificación de la prioridad
Impacto 4 × Probabilidad 3 = **12** → regla: P1.

Si el clasificador falla, un flaky podría mostrarse como PASS limpio y ocultar inestabilidad.

## Precondiciones
- Entorno Python del proyecto instalado; sin red (sockets deshabilitados en la suite unitaria).

## Datos de entrada
- [pass] → PASS
- [fail, pass] → FLAKY
- [fail, fail, fail] → FAIL
- [skip] → SKIPPED
- [blocked] → BLOCKED
- caso especificado sin intentos → NOT_RUN

## Pasos
1. Invocar el clasificador con cada secuencia sintética.

## Resultado esperado
- Estado final esperado en cada fila.

## Criterio de aceptación
Clasificación == tabla.

## Evidencias esperadas
- Resultado JUnit/JSON de pytest
- Mensaje de aserción con entrada, esperado y actual

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-FW-001")`; no se mantiene a mano.
