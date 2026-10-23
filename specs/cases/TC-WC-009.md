---
id: TC-WC-009
title: Borrado total del texto
requirement_ids:
- REQ-WC-001
- REQ-WC-002
- REQ-WC-003
priority: P1
test_type: functional
level: e2e
automation: planned
risk: medium
risk_assessment:
  impact: 3
  likelihood: 3
  score: 9
  computed_priority: P1
techniques:
- Valores límite
- Transición de estados
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

# TC-WC-009 — Borrado total del texto

## Objetivo
Verificar que al vaciar el editor los contadores vuelven a cero y Keyword Density queda vacía.

## Justificación de la prioridad
Impacto 3 × Probabilidad 3 = **9** → regla: P1.

Valor límite inferior; detecta contadores que no se reinician.

## Precondiciones
- Navegador Chrome headless con perfil temporal nuevo (sin localStorage ni cookies previos).
- Probe de disponibilidad de https://wordcounter.net/ exitoso; si falla, el caso se marca BLOCKED (ver SDD §5.6).
- Configuración por defecto del sitio, sin modificar opciones (REQ-WC-004).

## Datos de entrada
- Texto inicial `uno dos tres`; luego vaciar el editor

## Pasos
1. Abrir un WebDriver nuevo (fixture de alcance function) y navegar a https://wordcounter.net/.
2. Esperar con Expected Conditions a que el editor sea interactuable.
3. Limpiar el editor.
4. Ingresar el texto y esperar contadores.
5. Borrar todo el contenido.
6. Leer contadores y Keyword Density.

## Resultado esperado
- Palabras = 0, caracteres = 0, Keyword Density sin entradas.

## Criterio de aceptación
Los tres indicadores reflejan el estado vacío.

## Evidencias esperadas
- Registro estructurado por intento (JSON normalizado)
- Ante fallo: screenshot PNG + HTML del DOM + mensaje esperado/actual
- Versión de navegador y driver en el resultado de la ejecución

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-WC-009")`; no se mantiene a mano.
