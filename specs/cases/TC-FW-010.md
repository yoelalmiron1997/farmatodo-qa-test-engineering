---
id: TC-FW-010
title: Plugin de recolección registra cada intento
requirement_ids:
- REQ-QA-001
- REQ-QA-005
priority: P1
test_type: functional
level: integration
automation: planned
risk: medium
risk_assessment:
  impact: 4
  likelihood: 3
  score: 12
  computed_priority: P1
techniques:
- Prueba de integración con pytester
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

# TC-FW-010 — Plugin de recolección registra cada intento

## Objetivo
Verificar que el plugin registra un registro por intento (incluidos reintentos de pytest-rerunfailures), el Case ID y el estado BLOCKED.

## Justificación de la prioridad
Impacto 4 × Probabilidad 3 = **12** → regla: P1.

Sin registros por intento no hay detección de flaky; se prueba con una suite sintética determinista, sin navegador.

## Precondiciones
- Entorno Python del proyecto instalado; sin red (sockets deshabilitados en la suite unitaria).

## Datos de entrada
- Suite sintética: test que pasa, test que falla y luego pasa (contador en archivo), test que siempre falla, test BLOCKED, test sin marker

## Pasos
1. Ejecutar la suite sintética con pytester y `--reruns 2`.
2. Leer el JSONL de intentos.
3. Normalizar y clasificar.

## Resultado esperado
- PASS, FLAKY (2 intentos), FAIL (3 intentos), BLOCKED; el test sin marker queda con case_id nulo y lo detecta la validación.

## Criterio de aceptación
Registros e intentos == esperados.

## Evidencias esperadas
- Resultado JUnit/JSON de pytest
- Mensaje de aserción con entrada, esperado y actual

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-FW-010")`; no se mantiene a mano.
