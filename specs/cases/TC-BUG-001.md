---
id: TC-BUG-001
title: Exploración funcional de WordCounter (charter)
requirement_ids:
- REQ-BUG-001
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
- Exploratory testing basado en charters
- Heurísticas SFDPOT
mandatory_deliverable: true
external_dependencies:
- wordcounter.net
hypotheses:
- H-01
- H-02
- H-03
- H-05
- H-08
tags:
- manual
- exploratory
status: draft
spec_version: 1
---

# TC-BUG-001 — Exploración funcional de WordCounter (charter)

## Objetivo
Descubrir defectos y oportunidades de mejora de WordCounter con sesiones de exploración acotadas.

## Justificación de la prioridad
Impacto 4 × Probabilidad 3 = **12** → regla: P1.

Ejercicio 2 obligatorio. La exploración también confirma las hipótesis H-01…H-08 que alimentan el oráculo.

## Precondiciones
- Chrome actualizado, perfil limpio; desktop 1366×768 y emulación móvil 390×844.
- Sin modificar opciones para hallazgos del contador (las opciones pueden explorarse aparte, rotuladas).

## Datos de entrada
- Textos del catálogo de casos WC
- Textos reales en español con puntuación, acentos, emojis, multilínea

## Pasos
1. Sesión 1 (45 min): contadores con datos de borde.
2. Sesión 2 (45 min): Keyword Density (filtros, empates, actualización).
3. Sesión 3 (30 min): persistencia (autosave), responsive y accesibilidad básica.
4. Reproducir cada hallazgo al menos dos veces y capturar evidencia.
5. Registrar en `docs/bugs/BUG-WC-NNN.md` con la plantilla del SDD §9.3.

## Resultado esperado
- Reporte breve de hallazgos verificables, separados en defectos y mejoras.

## Criterio de aceptación
Cada hallazgo cumple la plantilla y tiene evidencia; ninguno sin reproducir.

## Evidencias esperadas
- Screenshots/GIF
- Notas de sesión con hora y entorno

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-BUG-001")`; no se mantiene a mano.
