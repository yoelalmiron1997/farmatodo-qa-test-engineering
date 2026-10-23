---
id: TC-ALG-009
title: Histograma
requirement_ids:
- REQ-ALG-005
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
- Golden file
mandatory_deliverable: false
external_dependencies:
- Ninguna externa
hypotheses: []
tags:
- algorithm
status: draft
spec_version: 1
---

# TC-ALG-009 — Histograma

## Objetivo
Verificar que el histograma muestra cada palabra con barras proporcionales en el mismo orden.

## Justificación de la prioridad
Impacto 4 × Probabilidad 2 = **8** → regla: P1.

Salida exigida por el PDF; lógica de presentación separada del conteo.

## Precondiciones
- Entorno Python del proyecto instalado; sin red (sockets deshabilitados en la suite unitaria).

## Datos de entrada
- Frecuencias del ejemplo del PDF

## Pasos
1. Renderizar el histograma con ancho máximo fijo.
2. Comparar con el golden.

## Resultado esperado
- La palabra más frecuente ocupa el ancho máximo; las demás, proporcional redondeado; mismo orden que la lista.

## Criterio de aceptación
Render == golden.

## Evidencias esperadas
- Resultado JUnit/JSON de pytest
- Mensaje de aserción con entrada, esperado y actual

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-ALG-009")`; no se mantiene a mano.
