---
id: TC-WC-004
title: Texto de ejemplo del PDF en WordCounter
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
  impact: 4
  likelihood: 3
  score: 12
  computed_priority: P1
techniques:
- Caracterización
- Consistencia entre ejercicios
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

# TC-WC-004 — Texto de ejemplo del PDF en WordCounter

## Objetivo
Comparar el comportamiento de WordCounter con el texto oficial del Ejercicio 4 (dos líneas).

## Justificación de la prioridad
Impacto 4 × Probabilidad 3 = **12** → regla: P1.

Une los Ejercicios 1 y 4: hace visibles las diferencias de regla (salto de línea, palabras cortas) entre el sitio y nuestra especificación. Spike: el sitio da 14 palabras y 99 caracteres (no cuenta el salto de línea, igual que el PDF), pero desempata por orden de aparición: muestra `tu` antes que `salud`, a diferencia del Ejercicio 4.

## Precondiciones
- Navegador Chrome headless con perfil temporal nuevo (sin localStorage ni cookies previos).
- Probe de disponibilidad de https://wordcounter.net/ exitoso; si falla, el caso se marca BLOCKED (ver SDD §5.6).
- Configuración por defecto del sitio, sin modificar opciones (REQ-WC-004).

## Datos de entrada
- Archivo `data/samples/farmatodo_example.txt` (2 líneas, sin línea final vacía)

## Pasos
1. Abrir un WebDriver nuevo (fixture de alcance function) y navegar a https://wordcounter.net/.
2. Esperar con Expected Conditions a que el editor sea interactuable.
3. Limpiar el editor.
4. Ingresar el contenido respetando el salto de línea.
5. Leer palabras, caracteres y top-3 de Keyword Density.
6. Comparar con el oráculo configurado con el perfil de reglas de WordCounter confirmado en la exploración.

## Resultado esperado
- Palabras = 14.
- Caracteres = 99 (los saltos de línea no se cuentan).
- Top-3: farmatodo 6, cuida 3, tu 2 (empate con salud resuelto por primera aparición).

## Criterio de aceptación
Valores visibles == oráculo con el perfil confirmado; la diferencia con el Ejercicio 4 queda documentada.

## Evidencias esperadas
- Registro estructurado por intento (JSON normalizado)
- Ante fallo: screenshot PNG + HTML del DOM + mensaje esperado/actual
- Versión de navegador y driver en el resultado de la ejecución

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-WC-004")`; no se mantiene a mano.
