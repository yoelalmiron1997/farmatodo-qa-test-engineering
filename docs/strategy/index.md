# Estrategia de pruebas

La fuente completa es el [SDD](../generated/sdd.md). Esta página resume las decisiones que guían todo lo demás.

## Especificación primero
Cada caso es un archivo `specs/cases/TC-*.md` con metadatos YAML (prioridad, riesgo, nivel, requisitos) y su descripción en Markdown. El catálogo, la matriz de trazabilidad, las páginas de cada caso y los indicadores de cobertura **se generan** a partir de esas fuentes. El CI falla ante cualquier divergencia (`qa specs validate`): IDs duplicados, casos huérfanos, prioridad inconsistente con el riesgo, tests sin `@pytest.mark.case`, casos automatizables sin test o bloques del SDD desactualizados.

## Priorización por riesgo
Puntaje = Impacto (1–5) × Probabilidad (1–5). **P0** ≥ 15 · **P1** 8–14 · **P2** ≤ 7. Una prioridad distinta de la regla exige una justificación escrita, que el portal marca con `*`. Los entregables obligatorios del PDF se marcan aparte (`mandatory_deliverable`), para no inflar prioridades.

## Niveles

| Suite | Qué prueba | Dependencias | Cuándo corre |
|---|---|---|---|
| `tests/unit/product` | Algoritmo del Ejercicio 4 y oráculo | ninguna (red deshabilitada) | PR y `master` |
| `tests/unit/framework` | Clasificador flaky, métricas, gate, historial, validador, reporting | ninguna (red deshabilitada) | PR y `master` |
| `tests/integration` | Plugin de pytest (con `pytester`), README | sistema de archivos | PR y `master` |
| `tests/e2e` | wordcounter.net con Selenium | Chrome, Internet | `master`, manual y diaria |
| `tests/performance` | Mediciones P2 | Chrome, Internet | manual y semanal opcional |

## Aislamiento
- **Entre tests:** navegador y perfil nuevos por test, datos propios, orden aleatorio (`pytest-randomly`, con la semilla registrada) y ningún estado global mutable.
- **De los datos:** el oráculo calcula el esperado solo desde el texto de entrada; nunca lee la página.
- **Del reporting:** reportes, gate y portal consumen el resultado normalizado y se prueban con datos sintéticos.
- **De la infraestructura:** la suite unitaria corre sin Selenium, sin navegador y sin red (`pytest-socket`). El contrato de `import-linter` impide que el núcleo importe Selenium o pytest.
- **Límite explícito:** wordcounter.net y farmatodo.com no están bajo nuestro control. Sus caídas o cambios se vuelven observables (categorías de fallo, estado BLOCKED, entorno registrado), pero no evitables.

## Estado BLOCKED
Antes de cada test de UI, un *probe* HTTP verifica el sitio. Un error de red, HTTP 5xx o 429, o que el editor no aparezca al cargar, marcan el test como **BLOCKED** (no FAIL ni PASS). Un P0 bloqueado deja el gate **inconclusivo** y el job falla: nunca queda verde sin evidencia.
