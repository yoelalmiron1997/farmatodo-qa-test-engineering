---
id: TC-WC-003
title: Top 3 de Keyword Density sin empates
requirement_ids:
- REQ-WC-003
priority: P0
test_type: functional
level: e2e
automation: planned
risk: high
risk_assessment:
  impact: 5
  likelihood: 4
  score: 20
  computed_priority: P0
techniques:
- Partición de equivalencia
- Diseño de datos para orden inequívoco
mandatory_deliverable: false
external_dependencies:
- wordcounter.net (tercero, fuera de nuestro control)
- Google Chrome + driver resuelto por Selenium Manager
- Conexión a Internet
hypotheses: []
tags:
- wordcounter
- smoke
status: draft
spec_version: 1
---

# TC-WC-003 — Top 3 de Keyword Density sin empates

## Objetivo
Verificar que las tres primeras entradas de Keyword Density son las tres palabras más frecuentes con su cantidad correcta.

## Justificación de la prioridad
Impacto 5 × Probabilidad 4 = **20** → regla: P0.

Objetivo central del Ejercicio 1 y el de mayor probabilidad de falla: Keyword Density aplica filtros propios (stop words en inglés, números, palabras de una letra; confirmados en el spike del 2026-10-23). Se usan palabras de ≥4 letras, no stop words, con frecuencias distintas (5/3/2) para eliminar ambigüedad de orden; el segundo dato intercala apariciones para verificar que se ordena por frecuencia y no por posición.

## Precondiciones
- Navegador Chrome headless con perfil temporal nuevo (sin localStorage ni cookies previos).
- Probe de disponibilidad de https://wordcounter.net/ exitoso; si falla, el caso se marca BLOCKED (ver SDD §5.6).
- Configuración por defecto del sitio, sin modificar opciones (REQ-WC-004).

## Datos de entrada
- `naranja naranja naranja naranja naranja limon limon limon pera pera kiwi` → naranja 5, limon 3, pera 2
- `pera naranja limon naranja pera naranja limon naranja kiwi naranja limon` → naranja 5, limon 3, pera 2

## Pasos
1. Abrir un WebDriver nuevo (fixture de alcance function) y navegar a https://wordcounter.net/.
2. Esperar con Expected Conditions a que el editor sea interactuable.
3. Limpiar el editor.
4. Ingresar el texto parametrizado.
5. Esperar a que Keyword Density muestre al menos 3 entradas.
6. Leer palabra y cantidad de las 3 primeras entradas (sin usar el porcentaje como valor esperado).
7. Comparar con el top-3 del oráculo.

## Resultado esperado
- Entradas 1–3: (naranja, 5), (limon, 3), (pera, 2), en ese orden.

## Criterio de aceptación
Las tres tuplas (palabra, cantidad) coinciden en valor y orden con el oráculo.

## Evidencias esperadas
- Registro estructurado por intento (JSON normalizado)
- Ante fallo: screenshot PNG + HTML del DOM + mensaje esperado/actual
- Versión de navegador y driver en el resultado de la ejecución

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-WC-003")`; no se mantiene a mano.
