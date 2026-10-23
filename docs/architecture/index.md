# Arquitectura

**Núcleo puro + adaptadores delgados.** Todo lo que decide (oráculo, algoritmo, clasificación, métricas, gate, trazabilidad, modelo del dashboard) es Python puro, sin Selenium, pytest, red ni disco. La infraestructura traduce desde y hacia ese núcleo. La regla de dependencias se **verifica** en CI con `import-linter` (`uv run lint-imports`).

## Componentes y dependencias (SOLID)

```mermaid
flowchart LR
  subgraph ENTRY["Entradas"]
    T["tests/ (pytest)"]
    CLI["qa CLI · composition root"]
    W4["word-frequency CLI"]
  end
  subgraph ADP["Adaptadores"]
    BF["ui.browser.BrowserFactory<br/>registro por nombre (OCP)"]
    PO["ui.pages.WordCounterPage<br/>+ KeywordDensityPanel"]
    PL["pytest_plugin<br/>QACollector + fixtures"]
    SL["specs.loader + implementation_scan"]
    FS["history.FileSystemHistoryRepository"]
    PR["reporting.portal"]
  end
  subgraph CORE["Núcleo puro"]
    OR["oracles.TextOracle + RuleProfile"]
    WF["word_frequency"]
    RM["results: modelos + normalizer"]
    FL["metrics.flaky"]
    PF["metrics.performance"]
    SM["metrics.summary"]
    QG["quality_gate"]
    VA["specs.validator + traceability.catalog"]
    DM["reporting.dashboard_model / summary"]
    HP(["Protocol HistoryReader / HistoryWriter"])
  end
  T --> PO --> BF
  T --> OR
  T -. hooks .-> PL --> RM
  W4 --> WF
  CLI --> SL --> VA
  CLI --> RM --> FL & SM
  CLI --> QG
  CLI --> DM --> FL & PF
  CLI --> FS
  FS -. implementa .-> HP
  CLI --> PR --> DM
```

| Principio | Dónde se aplica | Cómo se verifica |
|---|---|---|
| **S** | Page Objects sin aserciones; oráculo sin Selenium; clasificador sin I/O; renderers sin cálculo; el plugin solo recolecta | Revisión de código + contratos de imports |
| **O** | Navegadores por registro (`BrowserFactory.register`); categorías de fallo y política del gate como datos; nuevos casos sin tocar el reporting | `test_categories_are_extensible_without_code_changes`, política alternativa en `test_quality_gate` |
| **L** | Repositorio de historial en disco y en memoria con la misma suite de contrato | `test_history_repository.py` parametrizado por implementación |
| **I** | `HistoryReader` y `HistoryWriter` separados; el renderer no conoce navegadores; el oráculo no conoce pytest | mypy `--strict` |
| **D** | El CLI (composition root) inyecta implementaciones; el núcleo no importa infraestructura | `import-linter`: 3 contratos |

**Sin sobreingeniería:** no hay interfaz para Page Objects (un solo sitio), ni *services* o *managers* genéricos, ni jerarquías de tests. Los `Protocol` existen solo donde hay sustitución real (persistencia).

## Ciclo de vida de un test E2E

```mermaid
sequenceDiagram
  autonumber
  participant P as pytest
  participant F as fixtures (scope=function)
  participant B as BrowserFactory
  participant Pg as WordCounterPage
  participant O as TextOracle
  participant C as QACollector
  P->>F: setup del intento n
  F->>F: probe HTTP · falla ⇒ BLOCKED
  F->>B: create(perfil temporal nuevo)
  F->>Pg: open() · editor no disponible ⇒ BLOCKED
  P->>Pg: type_text(texto)
  P->>O: esperado = f(texto, perfil)
  P->>Pg: poll_until(actual == esperado)
  P->>P: assert con mensaje esperado/actual
  P->>C: makereport / logreport (intento, resultado, excepción)
  alt fallo
    C->>C: captura PNG + DOM del intento
  end
  F->>F: teardown: quit() + borrar perfil
  Note over P,C: pytest-rerunfailures repite el ciclo completo con un navegador nuevo
```

## Flujo de datos de observabilidad

```mermaid
flowchart LR
  X["1 · Ejecución<br/>pytest"] --> R["2 · Recolección<br/>attempts.jsonl"] --> N["3 · Normalización<br/>RunResult"] --> V["4 · Validación<br/>schema v1"] --> P["5 · Persistencia<br/>qa-history"] --> A["6 · Agregación<br/>métricas y tendencias"] --> Z["7 · Visualización<br/>MkDocs"]
```

## CI/CD

```mermaid
flowchart TB
  PR["Pull request"] --> A["pr-checks<br/>ruff · mypy · import-linter · unit · integración · specs · mkdocs --strict"]
  A -->|merge| M["main"]
  M --> B["functional-tests<br/>unit + integración + E2E (reruns=2)"]
  B --> B1["results · reporte resumen · artifacts"]
  B1 --> B2["quality gate = estado del job"]
  B1 --> H[("rama qa-history")]
  S["manual / semanal"] --> C["performance"] --> H
  B -. workflow_run .-> D["deploy-pages"]
  C -. workflow_run .-> D
  M -->|docs/specs| D
  H --> D --> GP["GitHub Pages"]
```

## Persistencia histórica y despliegue

```mermaid
sequenceDiagram
  participant T as functional-tests (main)
  participant H as job persist-history
  participant G as rama qa-history
  participant D as deploy-pages
  participant P as GitHub Pages
  T->>H: artifact run-result.json
  H->>H: qa history save (O_EXCL: nunca sobrescribe)
  H->>G: commit + push (reintento con rebase ante carreras)
  D->>G: checkout de solo lectura
  D->>D: qa portal build + mkdocs build --strict
  D->>P: upload-pages-artifact → deploy-pages
```

## Estructura del repositorio

```text
specs/            fuente: SDD, requisitos, casos TC-*.md, ADRs
config/           política del quality gate
src/farmatodo_qa/ word_frequency · oracles · results · metrics · quality_gate · specs · traceability
                  history · reporting · ui (Selenium) · pytest_plugin · config · cli
tests/            unit/{product,framework} · integration · e2e · performance · support
data/             ejemplo del PDF y observaciones del spike
docs/             portal editable (bugs, ux, estrategia, arquitectura…) + generated/ (no versionado)
.github/          workflows y Dependabot
```
