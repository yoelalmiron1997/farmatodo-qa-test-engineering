---
id: TC-ALG-003
title: Conteo de caracteres sin saltos de línea
requirement_ids:
- REQ-ALG-004
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
- Partición de equivalencia
- Valores límite
mandatory_deliverable: false
external_dependencies:
- Ninguna externa
hypotheses: []
tags:
- algorithm
status: draft
spec_version: 1
---

# TC-ALG-003 — Conteo de caracteres sin saltos de línea

## Objetivo
Verificar que se cuentan espacios y tabulaciones pero no `\n` ni `\r`.

## Justificación de la prioridad
Impacto 5 × Probabilidad 3 = **15** → regla: P0.

Regla explícita del PDF y fuente frecuente de errores entre sistemas operativos (CRLF).

## Precondiciones
- Entorno Python del proyecto instalado; sin red (sockets deshabilitados en la suite unitaria).

## Datos de entrada
- `ab\ncd` → 4
- `ab\r\ncd` → 4
- `a b` → 3
- `a\tb` → 3
- `abc\n` → 3

## Pasos
1. Invocar el análisis con cada texto.
2. Comparar el total de caracteres.

## Resultado esperado
- 4, 4, 3, 3 y 3 respectivamente.

## Criterio de aceptación
Total == esperado; CRLF y LF producen el mismo resultado.

## Evidencias esperadas
- Resultado JUnit/JSON de pytest
- Mensaje de aserción con entrada, esperado y actual

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-ALG-003")`; no se mantiene a mano.
