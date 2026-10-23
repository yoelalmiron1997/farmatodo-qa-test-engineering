---
id: TC-UX-001
title: UX de búsqueda de productos en Farmatodo
requirement_ids:
- REQ-UX-001
priority: P1
test_type: exploratory
level: manual
automation: manual
risk: medium
risk_assessment:
  impact: 4
  likelihood: 3
  score: 12
  computed_priority: P1
techniques:
- Evaluación heurística (Nielsen)
- Recorrido cognitivo
mandatory_deliverable: true
external_dependencies:
- farmatodo.com (tercero)
hypotheses:
- H-07
tags:
- manual
- ux
status: draft
spec_version: 1
---

# TC-UX-001 — UX de búsqueda de productos en Farmatodo

## Objetivo
Identificar problemas de UX en la búsqueda: sugerencias, tolerancia a errores ortográficos, resultados vacíos, filtros y orden.

## Justificación de la prioridad
Impacto 4 × Probabilidad 3 = **12** → regla: P1.

Ejercicio 3 obligatorio; la búsqueda es la entrada principal al catálogo.

## Precondiciones
- Acceso a https://www.farmatodo.com/ (documentar redirección por país, si existe — H-07).

## Datos de entrada
- Búsquedas: término exacto, con error ortográfico, sin tildes, sin resultados, término genérico

## Pasos
1. Ejecutar cada búsqueda en desktop.
2. Repetir en emulación móvil.
3. Registrar comportamiento, tiempos percibidos y mensajes.

## Resultado esperado
- Hallazgos candidatos con heurística violada, impacto y propuesta.

## Criterio de aceptación
Cada hallazgo es reproducible y tiene vista (desktop/responsive/mobile) y evidencia.

## Evidencias esperadas
- Screenshots anotados
- URL y hora

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-UX-001")`; no se mantiene a mano.
