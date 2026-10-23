---
id: TC-DEL-001
title: Reproducibilidad desde el README
requirement_ids:
- REQ-DEL-001
priority: P1
test_type: functional
level: integration
automation: planned
risk: medium
risk_assessment:
  impact: 5
  likelihood: 2
  score: 10
  computed_priority: P1
techniques:
- Prueba de humo en entorno limpio
mandatory_deliverable: true
external_dependencies:
- GitHub Actions
- PyPI
hypotheses: []
tags:
- delivery
status: draft
spec_version: 1
---

# TC-DEL-001 — Reproducibilidad desde el README

## Objetivo
Verificar que un clon limpio siguiendo el README instala dependencias, corre la suite unitaria y el algoritmo del Ejercicio 4.

## Justificación de la prioridad
Impacto 5 × Probabilidad 2 = **10** → regla: P1.

Requisito de entrega del PDF; se automatiza como job de CI en runner limpio con los mismos comandos del README.

## Precondiciones
- Runner limpio (ubuntu-latest) sin caché.

## Datos de entrada
- Comandos documentados en el README

## Pasos
1. Clonar el repositorio.
2. Ejecutar los comandos de instalación del README.
3. Ejecutar unit tests y la CLI con el ejemplo del PDF.

## Resultado esperado
- Todos los comandos terminan con código 0; la CLI imprime el golden.

## Criterio de aceptación
Job verde en runner limpio; cualquier divergencia entre README y comandos reales falla el job.

## Evidencias esperadas
- Log del job

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-DEL-001")`; no se mantiene a mano.
