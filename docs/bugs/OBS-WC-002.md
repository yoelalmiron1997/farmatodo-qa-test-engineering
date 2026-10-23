---
id: OBS-WC-002
title: La misma palabra en NFC y NFD se lista dos veces
type: improvement
priority: low
status: confirmed
related_cases: [TC-WC-012]
environment:
  os: Windows 10
  browser: Chromium 152.0.7977.167
  date: "2026-10-23"
---

# OBS-WC-002 — La misma palabra en NFC y NFD se lista dos veces

**Tipo:** oportunidad de mejora

`café` escrito con `é` precompuesto (NFC) y con `e` + acento combinante (NFD, frecuente en textos copiados desde macOS) aparece como **dos** entradas de 1 en Keyword Density, aunque se ven idénticas.

**Pasos:** cargar `café café` (la primera palabra en forma NFD) y observar Keyword Density.

**Sugerencia:** normalizar a NFC (`text.normalize('NFC')`) antes de contar. El algoritmo del Ejercicio 4 ya lo hace (TC-ALG-008).
