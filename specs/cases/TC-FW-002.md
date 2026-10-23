---
id: TC-FW-002
title: Agregación de indicadores y denominadores
requirement_ids:
- REQ-QA-001
- REQ-QA-005
- REQ-RPT-001
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
- Datos sintéticos
mandatory_deliverable: false
external_dependencies:
- Ninguna externa
hypotheses: []
tags:
- framework
- metrics
status: draft
spec_version: 1
---

# TC-FW-002 — Agregación de indicadores y denominadores

## Objetivo
Verificar fórmulas de indicadores y que intentos no se confunden con casos.

## Justificación de la prioridad
Impacto 4 × Probabilidad 3 = **12** → regla: P1.

Errores de denominador producen métricas engañosas en el dashboard.

## Precondiciones
- Entorno Python del proyecto instalado; sin red (sockets deshabilitados en la suite unitaria).

## Datos de entrada
- 10 casos especificados: 6 PASS (1 intento), 2 FLAKY (2 intentos c/u), 1 FAIL (3 intentos), 1 BLOCKED (0 intentos de cuerpo)

## Pasos
1. Agregar la ejecución sintética.
2. Comparar cada indicador con la fórmula del SDD Anexo A.6.

## Resultado esperado
- ejecutados = 9, intentos = 13, reintentos = 4, casos con reintento = 3, % flaky observado = 2/9 ≈ 22,2 %, bloqueados = 1

## Criterio de aceptación
Cada indicador == valor calculado a mano.

## Evidencias esperadas
- Resultado JUnit/JSON de pytest
- Mensaje de aserción con entrada, esperado y actual

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-FW-002")`; no se mantiene a mano.
