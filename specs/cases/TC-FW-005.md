---
id: TC-FW-005
title: Estadística de performance y baseline
requirement_ids:
- REQ-QA-002
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
mandatory_deliverable: false
external_dependencies:
- Ninguna externa
hypotheses: []
tags:
- framework
- performance
status: draft
spec_version: 1
---

# TC-FW-005 — Estadística de performance y baseline

## Objetivo
Verificar mín/media/mediana/máx/desvío, la regla de P95 y la comparación con baseline.

## Justificación de la prioridad
Impacto 3 × Probabilidad 2 = **6** → regla: P2.

Evita presentar percentiles no robustos o alertas falsas como regresiones.

## Precondiciones
- Entorno Python del proyecto instalado; sin red (sockets deshabilitados en la suite unitaria).

## Datos de entrada
- Muestras [100, 120, 110, 130, 90]
- n = 1 (sin desvío)
- n = 19 vs n = 20 (umbral de P95)

## Pasos
1. Calcular estadísticas.
2. Comparar contra baseline sintética.

## Resultado esperado
- P95 = no disponible con n < 20; alerta solo si se cumplen ambas condiciones del SDD Anexo D.4.

## Criterio de aceptación
Valores == esperados.

## Evidencias esperadas
- Resultado JUnit/JSON de pytest
- Mensaje de aserción con entrada, esperado y actual

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-FW-005")`; no se mantiene a mano.
