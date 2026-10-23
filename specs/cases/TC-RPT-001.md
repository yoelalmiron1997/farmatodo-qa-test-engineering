---
id: TC-RPT-001
title: Reporte resumen de ejecución
requirement_ids:
- REQ-RPT-001
- REQ-QA-005
priority: P0
test_type: functional
level: unit
automation: planned
risk: medium
risk_assessment:
  impact: 5
  likelihood: 2
  score: 10
  computed_priority: P1
priority_override_reason: 'Requisito explícitamente obligatorio del PDF: sin reporte resumen la entrega del Ejercicio 1 es incompleta, aunque la probabilidad de falla sea baja.'
techniques:
- Tabla de decisión
- Datos sintéticos
mandatory_deliverable: true
external_dependencies:
- Ninguna externa
hypotheses: []
tags:
- reporting
status: draft
spec_version: 1
---

# TC-RPT-001 — Reporte resumen de ejecución

## Objetivo
Verificar que el reporte resumen muestra ejecutados, aprobados y fallidos con la descripción de cada error.

## Justificación de la prioridad
Impacto 5 × Probabilidad 2 = **10** → regla: P1 · override a P0: Requisito explícitamente obligatorio del PDF: sin reporte resumen la entrega del Ejercicio 1 es incompleta, aunque la probabilidad de falla sea baja..

Exigencia literal del PDF. Se prueba con datos sintéticos (sin navegador) y además se verifica que cada ejecución real de CI produzca el reporte.

## Precondiciones
- Entorno Python del proyecto instalado; sin red (sockets deshabilitados en la suite unitaria).

## Datos de entrada
- Ejecución sintética: 3 PASS, 1 FLAKY, 2 FAIL (assertion y timeout), 1 SKIPPED, 1 BLOCKED

## Pasos
1. Construir el resultado normalizado sintético.
2. Renderizar el reporte resumen (Markdown y HTML).
3. Analizar el contenido generado.

## Resultado esperado
- Totales: ejecutados 6, aprobados 3, flaky 1, fallidos 2, omitidos 1, bloqueados 1 (definiciones del SDD Anexo A.6).
- Cada fallo lista Case ID, título, categoría y mensaje esperado/actual.
- El flaky aparece separado de los aprobados.

## Criterio de aceptación
Contenido renderizado == valores esperados; ningún flaky contabilizado como PASS limpio.

## Evidencias esperadas
- Resultado JUnit/JSON de pytest
- Mensaje de aserción con entrada, esperado y actual
- Reporte resumen publicado como artifact y en el Job Summary de cada ejecución real

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-RPT-001")`; no se mantiene a mano.
