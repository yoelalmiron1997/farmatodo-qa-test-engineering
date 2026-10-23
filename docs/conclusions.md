# Conclusiones

## ¿Qué requisitos cubrimos?
Los 16 requisitos del PDF y los 5 derivados de la consigna de ingeniería tienen casos o una verificación no basada en tests declarada (REQ-WC-004 por inspección, REQ-ALG-007 por análisis). Los cuatro ejercicios están completos: suite E2E con reporte resumen, reporte de fallas, análisis UX y algoritmo propio. El detalle vivo está en la [matriz de trazabilidad](generated/traceability.md).

## ¿Qué escenarios priorizamos?
Nueve P0: los tres objetivos de WordCounter con datos inequívocos, el reporte resumen exigido por el PDF, el núcleo del algoritmo (salida exacta, palabras, caracteres y orden) y el quality gate, porque un gate defectuoso oculta fallos. Los P1 cubren los bordes reales (espacios, puntuación, mayúsculas, acentos, multilínea, actualización) y los componentes del framework. Los P2, las caracterizaciones poco frecuentes, el volumen, la performance y la reproducción de defectos conocidos.

## ¿Qué problemas encontramos?
- **WordCounter:** cuatro defectos confirmados con evidencia. El más relevante es [BUG-WC-003](bugs/BUG-WC-003.md): Keyword Density no separa palabras unidas por NBSP, frecuente al pegar texto. Se suman dos oportunidades de mejora.
- **Farmatodo:** tres hallazgos UX. El más grave es [UX-FT-001](ux/UX-FT-001.md): entre 768 y 991 px el detalle de producto no muestra precio ni botón de compra.
- **Diferencia entre ejercicios:** WordCounter desempata por aparición y el PDF exige orden alfabético. Ambos coinciden en 14 palabras y 99 caracteres.

## ¿Qué limitaciones existen?
- Los sitios son de terceros: no se puede aislar su estado, publicidad ni disponibilidad. Se mitiga con el estado BLOCKED, categorías de fallo y entorno registrado.
- Las reglas de WordCounter no están documentadas: el oráculo modela 42 observaciones reales y los datos P0 son inequívocos.
- Los runners de GitHub están en EE. UU. y la exploración se hizo desde Argentina, por lo que el sitio podría variar por región.
- La performance se mide desde runners compartidos: es descriptiva, no representa usuarios reales.
- El checkout de Farmatodo exige cuenta: el análisis UX llega hasta ese paso.

## ¿Qué tan estable es la suite?
Se responde con datos, no con una afirmación: ver [Flaky tests](generated/flaky.md) y la [tendencia](index.md#tendencia). Al cerrar esta entrega:

- Las suites unitaria y de integración (186 tests al 2026-10-23, 90 % de cobertura de líneas del framework sin los adaptadores de UI) pasan en orden aleatorio y la unitaria sin red.
- La suite E2E se validó de punta a punta en un entorno sin acceso al sitio, donde se clasificó correctamente como BLOCKED con gate inconclusivo.
- Los localizadores, los eventos y el JavaScript de medición se verificaron en el sitio real durante el spike.

Las corridas reales contra wordcounter.net las ejecuta GitHub Actions, y su estabilidad se acumula en el historial.

## ¿Qué mejoraríamos?
- Ejecutar la suite E2E en Firefox (la fábrica ya lo admite) y en más resoluciones.
- Agregar regresión visual para los hallazgos responsive de Farmatodo (768–991 px).
- Compactar automáticamente el historial con un job mensual (hoy la política está documentada y la compactación es manual).
- Confirmar con el equipo las preguntas abiertas (desempate con acentos, formato del histograma) y ajustar las decisiones D-ALG-x si corresponde.
