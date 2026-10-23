---
id: TC-ALG-006
title: Errores de lectura
requirement_ids:
- REQ-ALG-001
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
- Adivinación de errores
mandatory_deliverable: false
external_dependencies:
- Ninguna externa
hypotheses: []
tags:
- algorithm
status: draft
spec_version: 1
---

# TC-ALG-006 — Errores de lectura

## Objetivo
Verificar mensajes claros y códigos de salida ante archivo inexistente o no decodificable como UTF-8.

## Justificación de la prioridad
Impacto 3 × Probabilidad 3 = **9** → regla: P1.

Robustez de la CLI entregable; evita trazas de Python como interfaz de usuario.

## Precondiciones
- Entorno Python del proyecto instalado; sin red (sockets deshabilitados en la suite unitaria).

## Datos de entrada
- Ruta inexistente
- Archivo con bytes inválidos en UTF-8
- Archivo UTF-8 con BOM

## Pasos
1. Ejecutar la CLI con cada entrada.
2. Capturar stderr y código de salida.

## Resultado esperado
- Inexistente → mensaje en stderr y código ≠ 0.
- No decodificable → mensaje en stderr y código ≠ 0.
- BOM → se ignora y no cuenta como carácter.

## Criterio de aceptación
Mensajes y códigos == esperados; sin traceback.

## Evidencias esperadas
- Resultado JUnit/JSON de pytest
- Mensaje de aserción con entrada, esperado y actual

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-ALG-006")`; no se mantiene a mano.
