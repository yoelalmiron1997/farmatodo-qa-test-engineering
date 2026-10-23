---
id: TC-WC-011
title: Empates en el top 3 de Keyword Density
requirement_ids:
- REQ-WC-003
priority: P2
test_type: functional
level: e2e
automation: planned
risk: low
risk_assessment:
  impact: 3
  likelihood: 2
  score: 6
  computed_priority: P2
techniques:
- Caracterización
- Valores límite
mandatory_deliverable: false
external_dependencies:
- wordcounter.net (tercero, fuera de nuestro control)
- Google Chrome + driver resuelto por Selenium Manager
- Conexión a Internet
hypotheses: []
tags:
- wordcounter
status: draft
spec_version: 1
---

# TC-WC-011 — Empates en el top 3 de Keyword Density

## Objetivo
Documentar cómo el sitio ordena palabras con la misma frecuencia.

## Justificación de la prioridad
Impacto 3 × Probabilidad 2 = **6** → regla: P2.

El PDF no define el desempate para el Ejercicio 1. El spike confirmó que el sitio ordena los empates por primera aparición; se fija como regresión.

## Precondiciones
- Navegador Chrome headless con perfil temporal nuevo (sin localStorage ni cookies previos).
- Probe de disponibilidad de https://wordcounter.net/ exitoso; si falla, el caso se marca BLOCKED (ver SDD §5.6).
- Configuración por defecto del sitio, sin modificar opciones (REQ-WC-004).

## Datos de entrada
- `beta beta alfa alfa gamma gamma delta` → empate triple en 2

## Pasos
1. Abrir un WebDriver nuevo (fixture de alcance function) y navegar a https://wordcounter.net/.
2. Esperar con Expected Conditions a que el editor sea interactuable.
3. Limpiar el editor.
4. Ingresar el texto.
5. Leer las 3 primeras entradas.

## Resultado esperado
- Entradas 1–3: (beta, 2), (alfa, 2), (gamma, 2): orden de primera aparición.

## Criterio de aceptación
Tuplas y orden == oráculo (perfil con desempate por primera aparición).

## Evidencias esperadas
- Registro estructurado por intento (JSON normalizado)
- Ante fallo: screenshot PNG + HTML del DOM + mensaje esperado/actual
- Versión de navegador y driver en el resultado de la ejecución

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-WC-011")`; no se mantiene a mano.
