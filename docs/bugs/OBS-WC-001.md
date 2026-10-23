---
id: OBS-WC-001
title: Lista de stop words incompleta e inconsistente
type: improvement
priority: low
status: confirmed
related_cases: [TC-WC-015]
environment:
  os: Windows 10
  browser: Chromium 152.0.7977.167
  date: "2026-10-23"
---

# OBS-WC-001 — Lista de *stop words* incompleta e inconsistente

**Tipo:** oportunidad de mejora

Con `should would could`, Keyword Density excluye `would` pero lista `should` y `could`. Las *stop words* en español (`el`, `la`, `de`, `que`, `tu`, `los`) nunca se excluyen, aunque el sitio ofrece idiomas.

**Pasos:** escribir `should would could` y, por separado, `el la de que y en`; observar Keyword Density.

**Sugerencia:** documentar la lista usada, completarla (incluir los verbos modales de forma coherente) y aplicar la lista del idioma del texto.
