---
id: TC-UX-003
title: UX de carrito y checkout en Farmatodo
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

# TC-UX-003 — UX de carrito y checkout en Farmatodo

## Objetivo
Evaluar agregar/quitar productos, cantidades, costos visibles y el ingreso al checkout hasta antes del pago.

## Justificación de la prioridad
Impacto 4 × Probabilidad 3 = **12** → regla: P1.

Ejercicio 3 obligatorio; mayor impacto de negocio (abandono de carrito).

## Precondiciones
- Sin compras reales ni datos de pago; si el checkout exige cuenta, se documenta el bloqueo o lo realiza el candidato con sus propios datos, que nunca aparecen en la evidencia.

## Datos de entrada
- Carrito con 2 productos

## Pasos
1. Agregar productos.
2. Modificar cantidades y eliminar.
3. Avanzar al checkout hasta el paso previo al pago.
4. Repetir en móvil.

## Resultado esperado
- Hallazgos candidatos documentados; bloqueos registrados.

## Criterio de aceptación
Igual que TC-UX-001.

## Evidencias esperadas
- Screenshots anotados (datos personales ocultos)

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-UX-003")`; no se mantiene a mano.
