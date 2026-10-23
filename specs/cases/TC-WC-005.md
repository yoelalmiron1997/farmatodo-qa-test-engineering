---
id: TC-WC-005
title: Espacios adicionales, iniciales y finales
requirement_ids:
- REQ-WC-001
- REQ-WC-002
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
- Valores límite
- Partición de equivalencia
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

# TC-WC-005 — Espacios adicionales, iniciales y finales

## Objetivo
Verificar que espacios múltiples no generan palabras vacías y que los caracteres cuentan cada espacio.

## Justificación de la prioridad
Impacto 4 × Probabilidad 3 = **12** → regla: P1.

Entrada muy frecuente al pegar texto; error clásico de tokenización (split por un único espacio).

## Precondiciones
- Navegador Chrome headless con perfil temporal nuevo (sin localStorage ni cookies previos).
- Probe de disponibilidad de https://wordcounter.net/ exitoso; si falla, el caso se marca BLOCKED (ver SDD §5.6).
- Configuración por defecto del sitio, sin modificar opciones (REQ-WC-004).

## Datos de entrada
- `  hola   mundo  ` → 2 palabras, 16 caracteres
- `hola  mundo` → 2 palabras, 11 caracteres

## Pasos
1. Abrir un WebDriver nuevo (fixture de alcance function) y navegar a https://wordcounter.net/.
2. Esperar con Expected Conditions a que el editor sea interactuable.
3. Limpiar el editor.
4. Ingresar el texto.
5. Leer contadores.
6. Comparar con el oráculo.

## Resultado esperado
- Palabras = 2 en ambos casos; caracteres = 16 y 11 (cada espacio cuenta).

## Criterio de aceptación
Valores visibles == oráculo.

## Evidencias esperadas
- Registro estructurado por intento (JSON normalizado)
- Ante fallo: screenshot PNG + HTML del DOM + mensaje esperado/actual
- Versión de navegador y driver en el resultado de la ejecución

## Implementación
Se vincula automáticamente mediante el marker `@pytest.mark.case("TC-WC-005")`; no se mantiene a mano.
