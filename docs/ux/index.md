# Experiencia de usuario — Farmatodo (Ejercicio 3)

**Fecha:** 2026-10-23 · **Sitio:** `www.farmatodo.com` → selector de país → `www.farmatodo.com.co` (e-commerce de Colombia) · **Navegador:** Chromium 152 (panel del escritorio de Claude, Windows 10) · **Vistas:** web desktop a 1366 px, desktop en ventana de ~800 px y responsive con emulación móvil de 375 px (agente Android). No se usó un dispositivo móvil real, por eso ningún hallazgo se rotula "mobile".

**Método:** evaluación heurística (10 heurísticas de Nielsen y criterios básicos de WCAG 2.2) sobre los flujos de búsqueda, detalle de producto, carrito y checkout (charters TC-UX-001…004). Cada hallazgo se reprodujo y se verificó en el DOM. Severidad según la escala de Nielsen (0–4).

**Bloqueos y límites (documentados, no omitidos):**

- `www.farmatodo.com` no es una tienda: es un selector de país. El análisis se hizo en el sitio de Colombia, el de mayor oferta online.
- El checkout exige iniciar sesión ("Ir a pagar" abre un modal de login). No se crearon cuentas ni se ingresaron datos personales, así que el análisis llega hasta ese paso.
- Se usó un producto con fórmula médica y se vació el carrito al terminar. No se hizo ninguna compra.

## Hallazgos principales

| ID | Vista | Flujo | Problema | Severidad |
|---|---|---|---|---|
| [UX-FT-001](UX-FT-001.md) | Web desktop (ventana de 768–991 px) | Detalle de producto | No se muestran ni el precio ni el botón de compra | 4 — catastrófico |
| [UX-FT-002](UX-FT-002.md) | Web desktop (~800 px) | Búsqueda | Los filtros no se reconocen como seleccionables y no funcionan con teclado | 3 — mayor |
| [UX-FT-003](UX-FT-003.md) | Web desktop (1366 px y ~800 px) | Carrito y checkout | Se agrega un medicamento con fórmula sin aviso y una bolsa que el usuario no pidió | 3 — mayor |

## Observaciones secundarias

No se cuentan entre los tres hallazgos, pero quedan registradas con evidencia:

- **Header a ~800 px:** los nombres de categorías quedan cortados debajo de la barra azul ("Cuidado del bebé", "Hogar, mascotas y otros"), la primera categoría se recorta por la izquierda y el botón *Prime* tapa el enlace *Cupones* ([captura](../assets/ux/UX-OBS-header-808px.png)).
- **Selector de país (`www.farmatodo.com`):** no declara `<meta name="viewport">`. En emulación móvil la página se renderiza a 981 px de ancho, y a 808 px el título se superpone al logo y desborda el recuadro ([808 px](../assets/ux/UX-00-selector-808px.jpg), [375 px](../assets/ux/UX-00-selector-mobile-375.jpg)).
- **Carrito a ~800 px:** el distintivo de reCAPTCHA tapa la etiqueta "Total" del resumen ([captura](../assets/ux/UX-FT-003-carrito-808px.jpg)).
- **Accesibilidad:** el ícono del carrito, los botones de Google/Apple, los controles de cantidad y el de eliminar no tienen nombre accesible. La tecla Escape no cierra el modal de login.
- **Búsqueda con error ortográfico:** `ibuprofneo` devuelve resultados de ibuprofeno (bien), pero el título muestra el término mal escrito sin un "¿Quisiste decir *ibuprofeno*?".
