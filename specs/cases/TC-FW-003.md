---
id: TC-FW-003
title: Repositorio de historial
requirement_ids:
- REQ-QA-004
- REQ-QA-005
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
- Prueba de contrato
- Doble de prueba
mandatory_deliverable: false
external_dependencies:
- Ninguna externa
hypotheses: []
tags:
- framework
- history
status: draft
spec_version: 1
---

# TC-FW-003 — Repositorio de historial

## Objetivo
Verificar guardado, lectura, idempotencia por (run_id, run_attempt) y funcionamiento con historial vacío.

## Justificación de la prioridad
Impacto 3 × Probabilidad 3 = **9** → regla: P1.

El historial es la fuente de tendencias; perder o duplicar registros invalida el portal.

## Precondiciones
- Entorno Python del proyecto instalado; sin red (sockets deshabilitados en la suite unitaria).

## Datos de entrada
- Directorio temporal vacío
- Dos ejecuciones distintas
- La misma ejecución guardada dos veces

## Pasos
1. Guardar y leer con la implementación en sistema de archivos.
2. Ejecutar la misma suite de contrato contra la implementación en memoria.

## Resultado esperado
- Historial vacío → lista vacía.
- Duplicado → rechazado sin sobrescribir.
- Lectura ordenada por fecha.

## Criterio de aceptación
Ambas implementaciones pasan la misma suite de contrato (LSP).

## Evidencias esperadas
- Resultado JUnit/JSON de pytest
- Mensaje de aserción con entrada, esperado y actual

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-FW-003")`; no se mantiene a mano.
