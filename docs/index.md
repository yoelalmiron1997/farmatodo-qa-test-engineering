# Quality Dashboard

Prueba técnica de **Ingeniero de Calidad QA — Farmatodo**, resuelta como un framework de calidad: **especificación primero (SDD) → pruebas aisladas y priorizadas por riesgo → GitHub Actions → métricas → este portal**.

| Ejercicio | Entregable | Dónde verlo |
|---|---|---|
| 1. Suite automatizada sobre wordcounter.net | Selenium + Pytest, 20 casos E2E, reporte resumen por corrida | [Casos](generated/test-cases.md) · [Ejecución](generated/execution.md) |
| 2. Reporte de fallas de wordcounter.net | 4 defectos confirmados y 2 mejoras, con evidencia | [Bugs](bugs/index.md) |
| 3. UX de Farmatodo | 3 hallazgos con vista, réplica, evidencia y propuesta | [UX](ux/index.md) |
| 4. Contador de frecuencia de palabras | Algoritmo propio, salida exacta del PDF, complejidad | [Algoritmo](algorithm.md) |

!!! note "Cómo leer este tablero"
    Los datos de ejecución provienen de la rama `qa-history`, que GitHub Actions alimenta en cada corrida de `main`. Un despliegue exitoso del portal **no** implica que las pruebas hayan pasado: el estado real es el del *quality gate* de cada corrida.

--8<-- "docs/generated/dashboard.md"
