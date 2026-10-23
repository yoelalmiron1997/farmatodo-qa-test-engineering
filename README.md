# Farmatodo QA Engineering & Quality Intelligence Platform

Prueba técnica de **Ingeniero de Calidad QA — Farmatodo**, resuelta como un framework de calidad: la especificación va primero, las pruebas están aisladas y priorizadas por riesgo, GitHub Actions las ejecuta y publica un portal con trazabilidad, flaky tests y performance.

[![pr-checks](https://github.com/yoelalmiron1997/farmatodo-qa-test-engineering/actions/workflows/pr-checks.yml/badge.svg?branch=master)](https://github.com/yoelalmiron1997/farmatodo-qa-test-engineering/actions/workflows/pr-checks.yml)
[![functional-tests](https://github.com/yoelalmiron1997/farmatodo-qa-test-engineering/actions/workflows/functional-tests.yml/badge.svg?branch=master)](https://github.com/yoelalmiron1997/farmatodo-qa-test-engineering/actions/workflows/functional-tests.yml)
[![deploy-pages](https://github.com/yoelalmiron1997/farmatodo-qa-test-engineering/actions/workflows/deploy-pages.yml/badge.svg?branch=master)](https://github.com/yoelalmiron1997/farmatodo-qa-test-engineering/actions/workflows/deploy-pages.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

- **Portal de calidad:** https://yoelalmiron1997.github.io/farmatodo-qa-test-engineering/
- **Especificación (SDD):** [`specs/SDD.md`](specs/SDD.md) · casos en [`specs/cases/`](specs/cases/) · requisitos en [`specs/requirements/requirements.yaml`](specs/requirements/requirements.yaml)

## Los cuatro ejercicios

| # | Ejercicio | Resultado |
|---|---|---|
| 1 | Suite automatizada de wordcounter.net (palabras, caracteres, top 3 de Keyword Density) + reporte resumen | Selenium + Pytest + Page Object Model; 20 casos E2E con oráculo independiente; reporte resumen por corrida (`reports/summary.md` / `.html` y Job Summary) |
| 2 | Reporte de fallas de wordcounter.net | 4 defectos confirmados y 2 mejoras, con pasos y capturas: [`docs/bugs/`](docs/bugs/index.md) |
| 3 | 3 problemas de UX en farmatodo.com | Con vista, réplica, evidencia y propuesta: [`docs/ux/`](docs/ux/index.md) |
| 4 | Contador de frecuencia de palabras | Algoritmo propio con la salida exacta del PDF y su complejidad: [`docs/algorithm.md`](docs/algorithm.md) |

## Cómo funciona

```mermaid
flowchart LR
  SDD["SDD + casos<br/>(Markdown + YAML)"] --> T["Tests<br/>unit · integración · E2E · performance"]
  T --> GA["GitHub Actions"]
  GA --> M["Métricas<br/>resultado normalizado + quality gate"]
  M --> H[("rama qa-history")]
  H --> D["Dashboard<br/>MkDocs Material"]
  SDD --> D
  D --> GP["GitHub Pages"]
```

- **Especificación como fuente única.** Cada caso (`specs/cases/TC-*.md`) declara requisitos, riesgo (impacto × probabilidad), prioridad, nivel y pasos. El catálogo, la matriz de trazabilidad y las páginas del portal se generan desde ahí, y `qa specs validate` falla ante cualquier inconsistencia.
- **Aislamiento.** Navegador y perfil nuevos por test; orden aleatorio; el oráculo calcula el esperado solo desde el texto de entrada; la suite unitaria corre sin red ni Selenium; un contrato de `import-linter` impide que el núcleo dependa de la infraestructura.
- **Flaky tests visibles.** Cada intento se registra. Un test que falla y luego pasa es FLAKY, nunca PASS. Las caídas del sitio son BLOCKED, no FAIL. El quality gate (`config/quality-gate.yaml`) decide el estado del job.

## Tecnologías

Las versiones son las del lockfile (`uv.lock`): local y CI usan exactamente las mismas.

| Área | Tecnología | Versión | Para qué se usa |
|---|---|---|---|
| Lenguaje y entorno | [Python](https://www.python.org/) | 3.12 | Todo el framework y el algoritmo del ejercicio 4 |
| | [uv](https://docs.astral.sh/uv/) | — | Instala Python y dependencias desde el lockfile: un solo comando, el mismo resultado en cualquier máquina |
| Automatización UI | [Selenium WebDriver](https://www.selenium.dev/) | 4.51 | Pruebas E2E sobre wordcounter.net con Page Object Model. Selenium Manager descarga el driver compatible con el Chrome instalado |
| Ejecución de pruebas | [Pytest](https://docs.pytest.org/) | 8.4 | Runner de unit, integración, E2E y performance. Un plugin propio registra cada intento, los estados y las evidencias |
| | [pytest-rerunfailures](https://github.com/pytest-dev/pytest-rerunfailures) | 16.7 | Reintentos en E2E. Un test que pasa al reintentar se marca FLAKY, no PASS |
| | [pytest-randomly](https://github.com/pytest-dev/pytest-randomly) | 5.0 | Orden aleatorio de los tests: detecta dependencias ocultas entre ellos |
| | [pytest-socket](https://github.com/miketheman/pytest-socket) | 0.8 | Bloquea la red en los tests unitarios: garantiza que no dependen de sitios externos |
| | [coverage.py](https://coverage.readthedocs.io/) | 7.17 | Cobertura de código del framework (90 %) |
| Modelos y datos | [Pydantic](https://docs.pydantic.dev/) | 2.14 | Valida los casos de prueba (YAML), los resultados de cada corrida (schema v1) y la política del quality gate |
| | [PyYAML](https://pyyaml.org/) | 6.0 | Lee el front matter de los casos `TC-*.md` y la configuración |
| Calidad de código | [Ruff](https://docs.astral.sh/ruff/) | 0.17 | Lint y formato |
| | [mypy](https://mypy-lang.org/) | 2.4 | Tipado estático en modo `--strict` |
| | [import-linter](https://import-linter.readthedocs.io/) | 2.15 | Tres contratos de arquitectura: el núcleo no puede importar Selenium, pytest ni infraestructura |
| Portal y reportes | [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) | 9.7 | Portal de calidad generado desde las specs y el historial |
| | [Mermaid](https://mermaid.js.org/) · [Chart.js](https://www.chartjs.org/) | — · 4.4 | Diagramas de arquitectura y gráficos de tendencia en el portal |
| | Chrome headless | — | Imprime el reporte resumen a PDF en CI |
| CI/CD | [GitHub Actions](https://docs.github.com/actions) | — | Seis workflows con acciones fijadas por SHA y permisos mínimos |
| | [GitHub Pages](https://pages.github.com/) | — | Publica el portal |
| | [Dependabot](https://docs.github.com/code-security/dependabot) | — | Propone actualizaciones de dependencias y acciones |

## Instalación

Requisitos: [uv](https://docs.astral.sh/uv/getting-started/installation/) y, para las pruebas de UI, Google Chrome (Selenium Manager descarga el driver compatible).

```bash
git clone https://github.com/yoelalmiron1997/farmatodo-qa-test-engineering.git
cd farmatodo-qa-test-engineering
uv sync --group dev            # crea .venv con Python 3.12 y las versiones del lockfile
```

## Ejecutar

| Qué | Comando |
|---|---|
| Ejercicio 4 con el ejemplo del PDF | `uv run word-frequency data/samples/farmatodo_example.txt` |
| … con histograma de barras | `uv run word-frequency data/samples/farmatodo_example.txt --histogram` |
| Tests unitarios (sin red ni navegador) | `uv run pytest tests/unit` |
| Unit + integración (lo que corre `pytest` a secas) | `uv run pytest` |
| E2E contra wordcounter.net (Selenium) | `uv run pytest tests/e2e` |
| E2E con reintentos y recolección de resultados | `uv run pytest tests/e2e --reruns 2 --qa-results-dir reports` |
| Performance (P2, secuencial, ligera) | `uv run pytest tests/performance -p no:randomly --qa-results-dir reports` |
| Validar especificaciones y trazabilidad | `uv run qa specs validate` |
| Regenerar los bloques generados del SDD | `uv run qa specs generate` |

Variables útiles: `QA_HEADLESS=false` (ver el navegador), `QA_TIMEOUT=15`, `QA_PERF_SAMPLES=5` (máximo 10), `QA_BASE_URL`, `QA_BROWSER` (`chrome` o `firefox`).

## Ejecuciones y reportes: dónde verlos

Cada push a `master`, la corrida diaria y la ejecución manual de `functional-tests` dejan sus resultados en cuatro lugares:

| Dónde | Qué hay | Cuánto dura |
|---|---|---|
| [**Portal → Quality Dashboard**](https://yoelalmiron1997.github.io/farmatodo-qa-test-engineering/) | Estado de la última corrida, quality gate, cobertura y tendencia. Detalle en [Test Execution](https://yoelalmiron1997.github.io/farmatodo-qa-test-engineering/generated/execution.html), [Flaky Tests](https://yoelalmiron1997.github.io/farmatodo-qa-test-engineering/generated/flaky.html) y [Performance](https://yoelalmiron1997.github.io/farmatodo-qa-test-engineering/generated/performance.html) | Siempre (se regenera tras cada corrida) |
| [**Actions → functional-tests**](https://github.com/yoelalmiron1997/farmatodo-qa-test-engineering/actions/workflows/functional-tests.yml) → abrir una corrida | El **reporte resumen** en la propia página de la corrida (*Summary*) | 90 días (logs de GitHub) |
| Misma corrida → sección *Artifacts* → **`functional-reports`** (zip) | Reporte resumen en **PDF**, HTML y Markdown, evidencias de cada fallo y datos crudos (ver tabla siguiente) | 30 días |
| Rama [**`qa-history`**](https://github.com/yoelalmiron1997/farmatodo-qa-test-engineering/tree/qa-history/runs) | Un JSON por corrida: `runs/<workflow>/<AAAA>/<MM>/<run_id>-<intento>.json`. Es la fuente de las tendencias del portal | Permanente |

`performance` funciona igual: [su workflow](https://github.com/yoelalmiron1997/farmatodo-qa-test-engineering/actions/workflows/performance.yml) y el artifact **`performance-reports`**.

Contenido del artifact (igual a la carpeta `reports/` cuando se corre en local):

| Archivo | Para qué |
|---|---|
| `summary.pdf` | Reporte resumen listo para compartir o imprimir |
| `summary.html` · `summary.md` | El mismo reporte en HTML y Markdown |
| `evidence/*.png` · `evidence/*.html` | Captura de pantalla y DOM de cada intento fallido |
| `run-result.json` | Resultado normalizado (schema v1) con estados, intentos, entorno y decisión del gate |
| `junit-unit.xml` · `junit-e2e.xml` | JUnit para cualquier herramienta de CI |
| `attempts.jsonl` · `session-*.json` | Registro crudo de cada intento, tal como lo recolectó el plugin |

En local, después de correr los tests con `--qa-results-dir reports`:

```bash
uv run qa results build --results-dir reports --out reports/run-result.json   # normaliza + evalúa el gate
uv run qa report summary --run reports/run-result.json --out-dir reports      # reports/summary.md y summary.html
uv run qa gate --run reports/run-result.json                                  # código de salida = decisión del gate
```

El **reporte resumen** muestra escenarios ejecutados, aprobados, flaky, fallidos, omitidos y bloqueados, y para cada fallo el caso, la categoría, la descripción del error y la evidencia (captura y DOM en `reports/evidence/`).

Para interpretar los resultados:

- *Aprobados* son PASS limpios, en el primer intento.
- *FLAKY* falló y luego pasó en la misma corrida: requiere atención y bloquea si es P0.
- *BLOCKED* indica que el sitio no estaba disponible antes del test: no es un fallo del producto, pero un P0 bloqueado deja el gate inconclusivo.
- Los casos TC-WC-017…020 reproducen defectos confirmados y fallan a propósito; el gate los muestra como *fallo conocido*.

## Documentación local

```bash
uv sync --group dev --group docs
uv run qa portal build          # genera docs/generated desde specs (y --history-dir si hay historial)
uv run mkdocs serve             # http://127.0.0.1:8000
```

## CI/CD

| Workflow | Cuándo | Qué hace |
|---|---|---|
| `pr-checks` | PR y push a `master` | ruff, formato, mypy, import-linter, `qa specs validate`, unit + integración con cobertura, `mkdocs build --strict`; job `readme-smoke` con estos comandos en un runner limpio |
| `functional-tests` | push a `master`, manual y diario | unit + integración sin reintentos; E2E headless con reintentos; resultado normalizado, reporte, artifacts, gate; persiste el historial |
| `performance` | manual y semanal | mediciones P2 secuenciales; persiste el historial |
| `deploy-pages` | cambios en docs/specs, fin de las corridas anteriores, manual | genera el portal desde specs + `qa-history` y lo publica con las acciones oficiales de Pages |
| `sync-develop` | push a `master` | avanza `develop` hasta `master` (o hace merge si `develop` divergió; nunca fuerza) |
| `persist-history` | reutilizable | agrega `runs/<workflow>/<AAAA>/<MM>/<run_id>-<intento>.json` a la rama `qa-history` sin sobrescribir |

**Ramas:** `master` es la rama principal y está protegida (solo cambios por pull request con los chequeos de `pr-checks` en verde, sin force-push ni borrado). `develop` se mantiene sincronizada con `master` automáticamente. `qa-history` solo la escribe CI.

Las acciones están fijadas por SHA de commit, con permisos mínimos por job y concurrencia controlada. Los PR nunca publican ni escriben historial.

**Para publicar el portal:** en *Settings → Pages*, elegir *Source: GitHub Actions*.

## Limitaciones

- wordcounter.net y farmatodo.com son sitios de terceros: su disponibilidad, publicidad y cambios no se controlan. Las caídas se registran como BLOCKED y los cambios de DOM, como fallos categorizados.
- Las reglas de conteo de WordCounter no están documentadas. El oráculo modela 42 observaciones reales (`data/observations/wordcounter-spike.json`) y se prueba contra ellas.
- Selenium no se comporta igual en todos los sistemas operativos. La referencia es Linux en GitHub Actions, y cada resultado registra las versiones de Python, Selenium y Chrome.
- La performance se mide desde runners compartidos: es descriptiva, sin SLA inventados.
- El checkout de Farmatodo requiere cuenta: el análisis UX llega hasta ese paso, sin crear cuentas ni comprar.

## Estructura

```text
specs/        SDD, requisitos, casos TC-*.md, decisiones (ADR)
config/       política del quality gate
src/          farmatodo_qa: algoritmo, oráculo, Page Objects, plugin de pytest, métricas, gate, historial, portal
tests/        unit/{product,framework} · integration · e2e · performance · support
data/         ejemplo del PDF, salida esperada y observaciones del spike
docs/         portal (bugs, ux, estrategia, arquitectura, algoritmo, conclusiones)
.github/      workflows y Dependabot
```

Licencia: MIT.
