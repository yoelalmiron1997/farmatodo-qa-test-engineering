---
id: TC-FW-009
title: Oráculo de WordCounter reproduce las observaciones del spike
requirement_ids:
- REQ-QA-005
- REQ-WC-001
- REQ-WC-002
- REQ-WC-003
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
- Prueba de contrato contra observaciones registradas
mandatory_deliverable: false
external_dependencies:
- Ninguna externa
hypotheses: []
tags:
- framework
- oracle
status: draft
spec_version: 1
---

# TC-FW-009 — Oráculo de WordCounter reproduce las observaciones del spike

## Objetivo
Verificar que el oráculo calcula, sin navegador, los mismos valores que el sitio mostró en la exploración para cada texto no defectuoso.

## Justificación de la prioridad
Impacto 4 × Probabilidad 3 = **12** → regla: P1.

Si el oráculo está mal, todos los E2E comparan contra un esperado incorrecto. Las observaciones del spike (`data/observations/wordcounter-spike.json`) son el contrato.

## Precondiciones
- Entorno Python del proyecto instalado; sin red (sockets deshabilitados en la suite unitaria).

## Datos de entrada
- 21 textos observados con palabras, caracteres y Keyword Density reales

## Pasos
1. Cargar las observaciones.
2. Calcular palabras, caracteres y Keyword Density con el oráculo.
3. Comparar (excluyendo las observaciones marcadas como defecto).

## Resultado esperado
- Coincidencia total para observaciones no defectuosas.

## Criterio de aceptación
Oráculo == observación.

## Evidencias esperadas
- Resultado JUnit/JSON de pytest
- Mensaje de aserción con entrada, esperado y actual

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-FW-009")`; no se mantiene a mano.
