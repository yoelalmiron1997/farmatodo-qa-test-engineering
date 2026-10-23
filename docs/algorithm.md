# Ejercicio 4 — Contador de frecuencia de palabras

Código: `src/farmatodo_qa/word_frequency/` (solo biblioteca estándar) · Pruebas: `tests/unit/product/test_word_frequency.py` (TC-ALG-001…011)

## Uso

```bash
uv run word-frequency data/samples/farmatodo_example.txt
uv run word-frequency data/samples/farmatodo_example.txt --histogram
python -m farmatodo_qa.word_frequency archivo.txt   # equivalente
```

Salida para el ejemplo del PDF (verificada byte a byte por TC-ALG-001):

```text
14 words
99 characters
farmatodo: 6
cuida: 3
salud: 2
tu: 2
toda: 1
```

Con `--histogram` se agregan barras proporcionales, en el mismo orden:

```text
farmatodo | ████████████████████████████████████████ 6
cuida     | ████████████████████ 3
salud     | █████████████ 2
tu        | █████████████ 2
toda      | ███████ 1
```

## Algoritmo

1. Leer el archivo **línea por línea** (UTF-8, descartando el BOM).
2. Por cada línea: contar los caracteres que no son `\n` ni `\r`; extraer las palabras con la expresión `[^\W_]+(?:['’\-][^\W_]+)*` sobre la forma NFC; pasarlas a minúsculas (`casefold`) y acumularlas en un diccionario.
3. Ordenar las entradas por `(-frecuencia, palabra)`.
4. Formatear la salida, separada del cálculo.

## Decisiones

| ID | Decisión | Motivo |
|---|---|---|
| D-ALG-1 | Palabra = letras o dígitos Unicode, con apóstrofo o guion internos; la puntuación no forma parte de la palabra; frecuencias sin distinguir mayúsculas y en NFC | `Hola`, `hola,` y `HOLA` son la misma palabra para el lector; `camión` no se parte en `cami` + `n` |
| D-ALG-2 | Desempate por punto de código de la forma normalizada | Determinista e independiente del *locale* del sistema (la alternativa con collation se dejó como pregunta al equipo) |
| D-ALG-3 | Salida por defecto idéntica al ejemplo; histograma gráfico con `--histogram` | El ejemplo es el criterio de aceptación literal; el histograma agrega sin romperlo |
| — | `\r\n` y `\n` son saltos de línea; la tabulación sí cuenta como carácter | El PDF excluye "saltos de línea", no espacios en blanco en general |

## Complejidad

Sea **N** la cantidad de caracteres de la entrada, **U** la de palabras distintas y **L** la longitud de la línea más larga.

- **Tiempo: O(N + U log U).** La tokenización y el conteo recorren cada carácter una vez (O(N)), con inserciones en el diccionario en O(1) amortizado. Ordenar las U entradas cuesta O(U log U). Como U ≤ N, en el peor caso es O(N log N); con vocabulario acotado, el costo es lineal en N.
- **Espacio: O(U + L).** El diccionario de frecuencias guarda U palabras, y en streaming solo hay una línea en memoria. El resultado ordenado ocupa O(U).

TC-ALG-010 lo verifica empíricamente: duplicar la entrada (100 000 → 200 000 palabras) aproximadamente duplica el tiempo. El test solo falla ante una razón mayor a 4×, que sería señal de comportamiento cuadrático.

## Diferencias con WordCounter

El sitio y este algoritmo siguen reglas distintas, y eso está documentado y probado: en el texto del PDF, WordCounter desempata por **orden de aparición** (`tu` antes que `salud`), mientras el PDF exige orden **alfabético** (`salud` antes que `tu`). Ambos coinciden en 14 palabras y 99 caracteres.
