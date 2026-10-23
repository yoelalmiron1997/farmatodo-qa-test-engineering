"""Perfiles de reglas declarativos para el oráculo.

``WORDCOUNTER_PROFILE`` modela el comportamiento **no defectuoso** observado en
wordcounter.net con su configuración por defecto durante el spike del 2026-10-23
(``data/observations/wordcounter-spike.json`` y ``docs/exploration/wordcounter-spike.md``).
Cada regla cita la observación que la sustenta. Donde el sitio se comporta de forma
inconsistente (defectos BUG-WC-00x), el perfil modela el comportamiento correcto.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from enum import StrEnum


class CharacterUnit(StrEnum):
    UTF16 = "utf16"  # unidades de código UTF-16, como ``String.length`` en JavaScript
    CODEPOINT = "codepoint"  # puntos de código Unicode (carácter percibido para BMP y emojis simples)


class TieBreak(StrEnum):
    FIRST_APPEARANCE = "first_appearance"
    ALPHABETICAL = "alphabetical"


@dataclass(frozen=True, slots=True)
class RuleProfile:
    """Reglas de conteo. Inmutable: los tests no pueden modificarlo por accidente."""

    name: str
    # Palabras -------------------------------------------------------------
    word_separator: re.Pattern[str]
    # Caracteres -----------------------------------------------------------
    character_unit: CharacterUnit
    excluded_characters: frozenset[str]
    # Keyword Density ------------------------------------------------------
    keyword_separator: re.Pattern[str]
    keyword_stop_words: frozenset[str]
    keyword_exclude_numeric: bool
    keyword_min_utf16_length: int
    keyword_tie_break: TieBreak


# Observaciones que sustentan cada regla (spike 2026-10-23):
# * Separadores de palabra: espacios (incl. NBSP y tab), "," entre letras ("hola,mundo" → 2;
#   "1,000" → 1), "/" ("hola/mundo" → 2) y "—" ("hola—mundo" → 2). El "." no separa
#   ("hola.mundo" → 1). Un token sin letras/dígitos/símbolos no cuenta ("---" → 0, "-" → no).
# * Caracteres: incluye espacios y tabulaciones; excluye "\n" y "\r" (PDF → 99; "hola\r\nmundo" → 9);
#   cuenta unidades UTF-16 ("hola 👋 mundo 🌎" → 16).
# * Keyword Density: minúsculas; puntuación en los bordes ignorada; el "." interno separa
#   ("hola.mundo" → hola, mundo); excluye stop words en inglés (the, and, i, am, a, an, it, is,
#   would, don't), números ("2026", "3.5", "1,000") y tokens de 1 unidad UTF-16 ("b c d" → vacío);
#   las stop words en español no se excluyen ("tu", "los", "el", "la"); empates por primera
#   aparición ("beta beta alfa alfa gamma gamma" → beta, alfa, gamma).
_OBSERVED_STOP_WORDS = frozenset({"the", "and", "i", "am", "a", "an", "it", "is", "would", "don't", "don’t"})

WORDCOUNTER_PROFILE = RuleProfile(
    name="wordcounter-default-2026-10-23",
    word_separator=re.compile(r"\s+|[/—]|(?<!\d),|,(?!\d)"),
    character_unit=CharacterUnit.UTF16,
    excluded_characters=frozenset("\r\n"),
    keyword_separator=re.compile(r"\s+|[/—.]|(?<!\d),|,(?!\d)"),
    keyword_stop_words=_OBSERVED_STOP_WORDS,
    keyword_exclude_numeric=True,
    keyword_min_utf16_length=2,
    keyword_tie_break=TieBreak.FIRST_APPEARANCE,
)

# Variante para afirmar el comportamiento correcto en BUG-WC-004 (emoji = 1 carácter).
CODEPOINT_CHARACTERS = replace(
    WORDCOUNTER_PROFILE, name="wordcounter-codepoints", character_unit=CharacterUnit.CODEPOINT
)
