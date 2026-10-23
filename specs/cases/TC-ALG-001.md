---
id: TC-ALG-001
title: Salida exacta del ejemplo del PDF
requirement_ids:
- REQ-ALG-001
- REQ-ALG-002
- REQ-ALG-003
- REQ-ALG-004
- REQ-ALG-006
- REQ-ALG-008
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
- Golden file
- Prueba basada en especificación
mandatory_deliverable: false
external_dependencies:
- Ninguna externa
hypotheses: []
tags:
- algorithm
- smoke
status: draft
spec_version: 1
---

# TC-ALG-001 — Salida exacta del ejemplo del PDF

## Objetivo
Verificar que la salida estándar coincide byte a byte con el ejemplo del PDF.

## Justificación de la prioridad
Impacto 5 × Probabilidad 3 = **15** → regla: P0.

Es el criterio de aceptación explícito del Ejercicio 4; cubre en una sola verificación lectura, conteos, frecuencias y orden.

## Precondiciones
- Entorno Python del proyecto instalado; sin red (sockets deshabilitados en la suite unitaria).

## Datos de entrada
- `data/samples/farmatodo_example.txt`
- Golden: `14 words`, `99 characters`, `farmatodo: 6`, `cuida: 3`, `salud: 2`, `tu: 2`, `toda: 1`

## Pasos
1. Ejecutar la CLI con el archivo de ejemplo capturando stdout.
2. Comparar con el golden file.

## Resultado esperado
- Salida idéntica a las 7 líneas del PDF.

## Criterio de aceptación
stdout == golden (byte a byte, incluido el salto final).

## Evidencias esperadas
- Resultado JUnit/JSON de pytest
- Mensaje de aserción con entrada, esperado y actual

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-ALG-001")`; no se mantiene a mano.
