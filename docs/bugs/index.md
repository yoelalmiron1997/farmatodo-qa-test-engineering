# Reporte de fallas — wordcounter.net (Ejercicio 2)

Exploración funcional con charters (TC-BUG-001) el 2026-10-23 sobre la configuración por defecto. Solo se reportan hallazgos reproducidos al menos dos veces, con evidencia. Los defectos tienen además un caso automatizado que los reproduce (TC-WC-017…020): falla mientras el defecto exista y el quality gate lo muestra como *fallo conocido*.

| ID | Tipo | Severidad | Título | Caso |
|---|---|---|---|---|
| [BUG-WC-001](BUG-WC-001.md) | Defecto | Menor | Contador y Keyword Density no coinciden ante un punto sin espacio | TC-WC-017 |
| [BUG-WC-002](BUG-WC-002.md) | Defecto | Menor | Un token formado solo por guiones aparece como palabra clave con 0 palabras | TC-WC-018 |
| [BUG-WC-003](BUG-WC-003.md) | Defecto | Mayor | Keyword Density no separa palabras unidas por espacio no separable (NBSP) | TC-WC-019 |
| [BUG-WC-004](BUG-WC-004.md) | Defecto | Menor | Cada emoji cuenta como 2 caracteres | TC-WC-020 |
| [OBS-WC-001](OBS-WC-001.md) | Mejora | — | Lista de *stop words* incompleta e inconsistente | — |
| [OBS-WC-002](OBS-WC-002.md) | Mejora | — | La misma palabra en NFC y NFD se lista dos veces | — |

**Escala de severidad:** *Mayor* — distorsiona el resultado principal de una función en un uso frecuente; *Menor* — resultado incorrecto o inconsistente en un caso poco frecuente, con impacto acotado; *Trivial* — cosmético.

**Entorno común:** Windows 10 · Chromium 152.0.7977.167 (panel del escritorio de Claude) · viewport 808 × 912 · configuración por defecto · 2026-10-23.
