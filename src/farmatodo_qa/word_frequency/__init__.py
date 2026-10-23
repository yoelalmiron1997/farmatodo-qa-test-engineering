"""Ejercicio 4 — contador de frecuencia de palabras.

Módulo autónomo: solo usa la biblioteca estándar y no comparte código con el oráculo
de WordCounter (contrato de import-linter), para que un defecto común no quede oculto.
"""

from farmatodo_qa.word_frequency.analyzer import TextStats, analyze, analyze_lines, count_characters, tokenize
from farmatodo_qa.word_frequency.render import render_histogram, render_report

__all__ = [
    "TextStats",
    "analyze",
    "analyze_lines",
    "count_characters",
    "render_histogram",
    "render_report",
    "tokenize",
]
