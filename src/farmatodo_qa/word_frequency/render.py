"""Presentación del resultado del Ejercicio 4 (separada del cálculo)."""

from __future__ import annotations

from collections.abc import Sequence

from farmatodo_qa.word_frequency.analyzer import TextStats


def _plural(count: int, singular: str, plural: str) -> str:
    return f"{count} {singular if count == 1 else plural}"


def render_report(stats: TextStats) -> str:
    """Formato exacto del ejemplo del PDF: totales y luego ``palabra: n`` por línea."""
    lines = [
        _plural(stats.words, "word", "words"),
        _plural(stats.characters, "character", "characters"),
        *(f"{word}: {count}" for word, count in stats.frequencies),
    ]
    return "\n".join(lines) + "\n"


def render_histogram(frequencies: Sequence[tuple[str, int]], width: int = 40, bar: str = "█") -> str:
    """Histograma horizontal: la palabra más frecuente ocupa ``width`` caracteres.

    Las barras son proporcionales (redondeo al entero más cercano, mínimo 1) y conservan
    el mismo orden que la lista de frecuencias.
    """
    if width < 1:
        raise ValueError("width debe ser >= 1")
    if not frequencies:
        return ""
    label_width = max(len(word) for word, _ in frequencies)
    top = frequencies[0][1]
    rows = []
    for word, count in frequencies:
        length = max(1, round(count / top * width))
        rows.append(f"{word.ljust(label_width)} | {bar * length} {count}")
    return "\n".join(rows) + "\n"
