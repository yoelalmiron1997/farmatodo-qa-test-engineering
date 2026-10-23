# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y versionado [SemVer](https://semver.org/lang/es/). Cada versión se publica como [release de GitHub](https://github.com/yoelalmiron1997/farmatodo-qa-test-engineering/releases) con su ambiente congelado.

## [1.0.0] — 2026-10-23

Entrega de la prueba técnica de Ingeniero de Calidad QA para Farmatodo.

### Agregado
- **Ejercicio 1:** suite E2E de wordcounter.net (Selenium + Pytest, Page Object Model, oráculo independiente) con reporte resumen en PDF, HTML y Markdown.
- **Ejercicio 2:** reporte de 4 defectos y 2 mejoras de WordCounter, cada defecto con un test que lo reproduce.
- **Ejercicio 3:** 3 hallazgos de UX en Farmatodo con evidencia y propuesta.
- **Ejercicio 4:** contador de frecuencia de palabras con la salida exacta del enunciado y análisis de complejidad.
- Especificación SDD: 21 requisitos, 51 casos priorizados por riesgo, 12 ADR y validación automática de trazabilidad.
- Clasificación de flaky tests, estado BLOCKED, quality gate declarativo e historial de ejecuciones en la rama `qa-history`.
- Portal de calidad en GitHub Pages y CI/CD con GitHub Actions.
- Reproducibilidad: Python 3.12.3 fijado, dependencias en `uv.lock`, versión de navegador fijable con `QA_BROWSER_VERSION` y workflow `release` que congela el ambiente en `environment.json`.
- Imagen Docker del ambiente congelado publicada en GitHub Packages (`ghcr.io/yoelalmiron1997/farmatodo-qa-test-engineering`).

[1.0.0]: https://github.com/yoelalmiron1997/farmatodo-qa-test-engineering/releases/tag/v1.0.0
