# Spike de exploración — wordcounter.net

**Fecha:** 2026-10-23 (03:00–03:15 UTC) · **Navegador:** Chromium 152.0.7977.167 (panel del escritorio de Claude, Windows 10) · **Configuración:** por defecto (Keyword Density `x1`) · **Datos crudos:** `data/observations/wordcounter-spike.json` (42 observaciones, versionadas en el repositorio)

Objetivo: resolver las hipótesis H-01…H-08 del SDD **antes** de escribir el oráculo y los Page Objects, y verificar los localizadores en el DOM real.

## Método

1. Inspección del DOM para localizar editor, contadores y Keyword Density.
2. Para cada texto de prueba: asignar `value` al `<textarea id="box">`, disparar el evento que usa el sitio y leer los contadores tras 1,1–1,5 s.
3. Confirmación con **tipeo real** (teclado) de tres textos, incluidos dos defectos.

## Localizadores verificados

| Elemento | Localizador | Nota |
|---|---|---|
| Editor | `#box` | `textarea`, placeholder "Start typing, or copy and paste…" |
| Encabezado | `#top_counter .counted` | texto "11 words 72 characters" |
| Palabras | `#word_count` | badge del panel *Details* |
| Caracteres | `#character_count` | badge del panel *Details* |
| Keyword Density | `#kwd-accordion-data a.list-group-item` | `span.word` + `span.badge` (" 5 (45%)") |

## Resultado de las hipótesis

| ID | Hipótesis | Resultado |
|---|---|---|
| H-01 | Separación de palabras | **Confirmada con matices.** Separan los espacios (incluidos NBSP, tab y em space), `,` entre letras, `/` y `—`. El `.` **no** separa (`hola.mundo` = 1). Un token sin letras ni dígitos no cuenta (`---` = 0; `hola - mundo` = 2). Los números cuentan como palabras. |
| H-02 | Caracteres | **Confirmada.** Incluye espacios y tabulaciones; **excluye `\n` y `\r`**: el texto del PDF da 99, igual que el Ejercicio 4. |
| H-03 | Keyword Density | **Confirmada.** Minúsculas; ignora la puntuación de los bordes; excluye *stop words* en inglés (`the`, `and`, `i`, `a`, `an`, `it`, `is`, `would`, `don't`…), números y tokens de una letra; **no** excluye stop words en español (`tu`, `los`, `el`). Empates por **orden de primera aparición** (en el texto del PDF muestra `tu` antes que `salud`, al revés que el Ejercicio 4). |
| H-04 | Evento de recálculo | **Refinada.** El sitio recalcula en **`keyup`**, no en `input` ni `change`. La inyección por JavaScript debe disparar `keyup`. Hay un *debounce*: la actualización llega ~305–311 ms después del evento (8 mediciones con `MutationObserver`). |
| H-05 | Persistencia | **Confirmada.** Guarda el texto en `localStorage["text"]`. Por eso cada test usa un perfil de navegador nuevo. |
| H-06 | Banners que cubren el editor | **No observado** desde Argentina. Hay 9 iframes publicitarios, ninguno sobre el editor. Se mantiene la detección de BLOCKED por si en CI (EE. UU.) aparece un interstitial. |
| H-07 | farmatodo.com | **Confirmada.** `www.farmatodo.com` es un selector de país (AR, CO, VE). El e-commerce evaluado es `www.farmatodo.com.co`. |
| H-08 | Unidad de caracteres | **Confirmada:** cuenta unidades UTF-16 (`hola 👋 mundo 🌎` = 16 en lugar de 14) → [BUG-WC-004](../bugs/BUG-WC-004.md). |

## Consecuencias en el diseño

- El oráculo (`farmatodo_qa.oracles`) modela estas reglas en un perfil declarativo y **reproduce las 42 observaciones** (TC-FW-009); en los casos defectuosos afirma el comportamiento correcto.
- Los datos P0 siguen siendo inequívocos: cualquier regla razonable da el mismo resultado.
- Diferencia documentada entre ejercicios: el desempate de WordCounter es por aparición; el del Ejercicio 4, alfabético (exigido por el PDF).
- Defectos encontrados: [BUG-WC-001…004](../bugs/index.md) y dos oportunidades de mejora (OBS-WC-001, 002).

## Limitaciones

Exploración desde un único navegador y región. Los valores de tiempo provienen del panel de escritorio y **no** se publican como mediciones de performance: esas se toman en CI (workflow `performance`).
