---
id: TC-UX-002
title: UX del detalle de producto en Farmatodo
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

# TC-UX-002 — UX del detalle de producto en Farmatodo

## Objetivo
Evaluar información de producto, precios, disponibilidad, imágenes y llamada a la acción.

## Justificación de la prioridad
Impacto 4 × Probabilidad 3 = **12** → regla: P1.

Ejercicio 3 obligatorio; vista de decisión de compra.

## Precondiciones
- Acceso al sitio; producto de venta libre (no requiere receta).

## Datos de entrada
- Dos productos de categorías distintas

## Pasos
1. Abrir el detalle desde la búsqueda.
2. Revisar jerarquía de información, CTA, variantes y mensajes.
3. Repetir en móvil.

## Resultado esperado
- Hallazgos candidatos documentados.

## Criterio de aceptación
Igual que TC-UX-001.

## Evidencias esperadas
- Screenshots anotados

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-UX-002")`; no se mantiene a mano.
