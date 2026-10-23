---
id: TC-UX-004
title: UX responsive y mobile en Farmatodo
requirement_ids:
- REQ-UX-001
priority: P1
test_type: exploratory
level: manual
automation: manual
risk: medium
risk_assessment:
  impact: 3
  likelihood: 3
  score: 9
  computed_priority: P1
techniques:
- Evaluación heurística
- Checklist WCAG 2.2 básico (tamaño de objetivo, contraste)
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

# TC-UX-004 — UX responsive y mobile en Farmatodo

## Objetivo
Evaluar adaptación de layout, navegación, tamaños de objetivo táctil y overlays en anchos 390, 768 y 1366 px.

## Justificación de la prioridad
Impacto 3 × Probabilidad 3 = **9** → regla: P1.

Ejercicio 3 pide indicar la vista; la mayoría del tráfico retail es móvil.

## Precondiciones
- DevTools con emulación de dispositivo; dispositivo real si está disponible (se indica cuál se usó).

## Datos de entrada
- Flujos de TC-UX-001…003

## Pasos
1. Recorrer los flujos en cada ancho.
2. Registrar desbordes, solapamientos y objetivos táctiles pequeños.

## Resultado esperado
- Hallazgos candidatos con vista explícita.

## Criterio de aceptación
Igual que TC-UX-001.

## Evidencias esperadas
- Screenshots por ancho

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-UX-004")`; no se mantiene a mano.
