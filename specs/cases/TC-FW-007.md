---
id: TC-FW-007
title: Datos del dashboard sin y con historial
requirement_ids:
- REQ-QA-004
- REQ-QA-005
priority: P2
test_type: functional
level: unit
automation: planned
risk: low
risk_assessment:
  impact: 3
  likelihood: 2
  score: 6
  computed_priority: P2
techniques:
- Valores límite
- Datos sintéticos
mandatory_deliverable: false
external_dependencies:
- Ninguna externa
hypotheses: []
tags:
- framework
- dashboard
status: draft
spec_version: 1
---

# TC-FW-007 — Datos del dashboard sin y con historial

## Objetivo
Verificar que el modelo del dashboard representa 'sin datos' en lugar de ceros cuando no hay ejecuciones.

## Justificación de la prioridad
Impacto 3 × Probabilidad 2 = **6** → regla: P2.

Evita mostrar métricas inventadas.

## Precondiciones
- Entorno Python del proyecto instalado; sin red (sockets deshabilitados en la suite unitaria).

## Datos de entrada
- Historial vacío
- Tres ejecuciones sintéticas

## Pasos
1. Generar el modelo del dashboard.

## Resultado esperado
- Vacío → indicadores en estado `no_data`.
- Con datos → tendencias de 3 puntos con fecha y commit.

## Criterio de aceptación
Modelo == esperado.

## Evidencias esperadas
- Resultado JUnit/JSON de pytest
- Mensaje de aserción con entrada, esperado y actual

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-FW-007")`; no se mantiene a mano.
