"""Conteo de palabras, caracteres y frecuencias (Ejercicio 4).

Decisiones de diseño (SDD §2.4):

* D-ALG-1 — Una palabra es una secuencia máxima de letras o dígitos Unicode, que puede
  contener apóstrofos o guiones *internos* (``don't``, ``e-commerce``). La puntuación no
  forma parte de la palabra. Las frecuencias son insensibles a mayúsculas (``casefold``)
  y se calculan sobre la forma normalizada NFC (``camión`` compuesto == descompuesto).
* D-ALG-2 — El desempate alfabético usa el orden de punto de código de la forma
  normalizada: determinista e independiente del *locale* del sistema.
* Caracteres: se cuentan todos los puntos de código del texto excepto ``\\n`` y ``\\r``.
  Los espacios y las tabulaciones sí cuentan. El BOM UTF-8 lo descarta la lectura.

Complejidad (N = caracteres de entrada, U = palabras distintas):

* Tiempo: O(N) para tokenizar y contar + O(U log U) para ordenar → O(N + U log U).
* Espacio: O(U) para el diccionario de frecuencias + O(L) para la línea en curso cuando
  se procesa en streaming con :func:`analyze_lines` (L = longitud de la línea más larga).
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass

# [^\W_] = letra o dígito Unicode (\w sin el guion bajo).
_WORD_RE = re.compile(r"[^\W_]+(?:['’\-][^\W_]+)*")
_LINE_BREAKS = frozenset("\r\n")


@dataclass(frozen=True, slots=True)
class TextStats:
    """Resultado inmutable del análisis de un texto."""

    words: int
    characters: int
    frequencies: tuple[tuple[str, int], ...]


def tokenize(text: str) -> list[str]:
    """Devuelve las palabras normalizadas (NFC + casefold) en orden de aparición."""
    normalized = unicodedata.normalize("NFC", text)
    return [match.group(0).casefold() for match in _WORD_RE.finditer(normalized)]


def count_characters(text: str) -> int:
    """Cuenta caracteres incluyendo espacios y excluyendo saltos de línea."""
    return sum(1 for char in text if char not in _LINE_BREAKS)


def sort_frequencies(counter: Counter[str]) -> tuple[tuple[str, int], ...]:
    """Ordena por ocurrencias descendentes y, en empate, alfabéticamente (D-ALG-2)."""
    return tuple(sorted(counter.items(), key=lambda item: (-item[1], item[0])))


def analyze_lines(lines: Iterable[str]) -> TextStats:
    """Analiza el texto línea por línea, sin cargarlo completo en memoria.

    Seguro para palabras que cruzan líneas: los saltos de línea siempre separan palabras,
    por lo que tokenizar cada línea por separado da el mismo resultado que el texto entero.
    """
    counter: Counter[str] = Counter()
    words = 0
    characters = 0
    for line in lines:
        tokens = tokenize(line)
        words += len(tokens)
        counter.update(tokens)
        characters += count_characters(line)
    return TextStats(words=words, characters=characters, frequencies=sort_frequencies(counter))


def analyze(text: str) -> TextStats:
    """Analiza un texto completo."""
    return analyze_lines(text.splitlines(keepends=True))
