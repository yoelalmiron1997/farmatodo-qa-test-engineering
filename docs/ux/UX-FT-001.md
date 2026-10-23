# UX-FT-001 — El detalle de producto no muestra precio ni botón de compra en ventanas de 768–991 px

**Vista:** web desktop con la ventana del navegador entre 768 y 991 px de ancho (pantalla dividida, laptop chica, zoom alto) · **Flujo:** detalle de producto · **Severidad:** 4 — catastrófico para ese segmento · **Caso:** TC-UX-002

## Qué está mal
En ese rango de anchos, la página de producto muestra imagen, descripción y ficha técnica, pero **no muestra el precio ni el botón "Agregar producto" en ningún lugar de la página**. El usuario no puede saber cuánto cuesta ni comprar. En móvil sí existe una barra fija con "Agregar producto", y desde 992 px aparece el bloque de compra de escritorio. En el medio no se muestra ninguno de los dos.

## Cómo replicarlo
1. En un navegador de escritorio, abrir `https://www.farmatodo.com.co/producto/1000591-ibuprofeno-genfar-800-mg-caja-x-50-tabletas`.
2. Reducir la ventana a unos 800 px de ancho (por ejemplo, ocupando la mitad de una pantalla de 1600 px).
3. Recorrer toda la página: no aparecen el precio ($17.560) ni el botón de compra.
4. Ensanchar la ventana a 992 px o más: el bloque de compra aparece a la derecha.

## Evidencia
| ~800 px (desktop): sin precio ni compra | 375 px (emulación móvil): barra "Agregar producto" | 1366 px: bloque de compra visible |
|---|---|---|
| ![808 px](../assets/ux/UX-FT-001-pdp-808px-sin-precio.jpg) | ![375 px](../assets/ux/UX-FT-001-pdp-mobile-375px.jpg) | ![1366 px](../assets/ux/UX-FT-001-pdp-1366px.jpg) |

**Verificación en el DOM (808 px):** el precio y el botón están dentro de un contenedor con las clases `col-12 col-lg-3 … d-none d-lg-block`, es decir, `display: none` por debajo del breakpoint `lg` (992 px). Ningún otro elemento visible de la página contiene un precio ni un botón "Agregar".

## Impacto
Bloquea la conversión: el usuario llega al producto desde la búsqueda y no puede completar la acción principal. Además viola las heurísticas *visibilidad del estado del sistema* y *control del usuario*: no hay indicio de que falte algo.

## Propuesta
- Mostrar un componente de compra en **todos** los anchos: la barra fija móvil por debajo de 992 px o el bloque de escritorio adaptado.
- Agregar pruebas de regresión visual en 768, 800, 900 y 991 px.
- Verificar en iPad: Safari en iPadOS se identifica como navegador de escritorio, por lo que podría caer en este rango. Es una hipótesis, no se probó.
