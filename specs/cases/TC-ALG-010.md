---
id: TC-ALG-010
title: Escalamiento lineal (informativo)
requirement_ids:
- REQ-ALG-007
priority: P2
test_type: non-functional
level: unit
automation: planned
risk: low
risk_assessment:
  impact: 2
  likelihood: 2
  score: 4
  computed_priority: P2
techniques:
- Análisis de complejidad
- Microbenchmark
mandatory_deliverable: false
external_dependencies:
- Ninguna externa
hypotheses: []
tags:
- algorithm
- benchmark
status: draft
spec_version: 1
---

# TC-ALG-010 — Escalamiento lineal (informativo)

## Objetivo
Aportar evidencia empírica de la complejidad documentada.

## Justificación de la prioridad
Impacto 2 × Probabilidad 2 = **4** → regla: P2.

Complementa el análisis teórico; no bloquea CI porque los tiempos dependen del runner.

## Precondiciones
- Entorno Python del proyecto instalado; sin red (sockets deshabilitados en la suite unitaria).

## Datos de entrada
- Textos sintéticos de 100k y 200k palabras con vocabulario fijo

## Pasos
1. Medir el tiempo de análisis de ambos tamaños (3 repeticiones, mediana).

## Resultado esperado
- Razón de tiempos aproximadamente lineal; se registra, no se afirma con umbral estricto.

## Criterio de aceptación
Registro de la medición; fallo solo si la razón supera 4× (señal de complejidad cuadrática).

## Evidencias esperadas
- Resultado JUnit/JSON de pytest
- Mensaje de aserción con entrada, esperado y actual

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-ALG-010")`; no se mantiene a mano.
