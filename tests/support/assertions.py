"""Comparación esperado (oráculo) vs. actual (Page Object) con mensajes descriptivos."""

from __future__ import annotations

from farmatodo_qa.oracles import TextOracle
from farmatodo_qa.ui.pages import WordCounterPage
from farmatodo_qa.ui.waits import poll_until


def assert_words(page: WordCounterPage, oracle: TextOracle, text: str, timeout_s: float) -> None:
    expected = oracle.word_count(text)
    actual = poll_until(lambda: page.counts().words, lambda v: v == expected, timeout_s)
    assert actual == expected, f"Palabras (panel Details) para {text!r}: esperado {expected}, actual {actual}"
    headline = page.headline_counts().words
    assert headline == expected, (
        f"Palabras (encabezado) para {text!r}: esperado {expected}, actual {headline}"
    )


def assert_characters(page: WordCounterPage, oracle: TextOracle, text: str, timeout_s: float) -> None:
    expected = oracle.character_count(text)
    actual = poll_until(lambda: page.counts().characters, lambda v: v == expected, timeout_s)
    assert actual == expected, (
        f"Caracteres (panel Details) para {text!r}: esperado {expected}, actual {actual}"
    )
    headline = page.headline_counts().characters
    assert headline == expected, (
        f"Caracteres (encabezado) para {text!r}: esperado {expected}, actual {headline}"
    )


def assert_top_keywords(
    page: WordCounterPage, oracle: TextOracle, text: str, timeout_s: float, n: int = 3
) -> None:
    expected = [str(k) for k in oracle.top_keywords(text, n)]
    actual = poll_until(
        lambda: [str(k) for k in page.keyword_density.top(n)], lambda v: v == expected, timeout_s
    )
    assert actual == expected, (
        f"Top-{n} de Keyword Density para {text!r}: esperado {expected}, actual {actual}"
    )


def assert_all_keywords(page: WordCounterPage, oracle: TextOracle, text: str, timeout_s: float) -> None:
    expected = [str(k) for k in oracle.keywords(text)]
    actual = poll_until(
        lambda: [str(k) for k in page.keyword_density.keywords()], lambda v: v == expected, timeout_s
    )
    assert actual == expected, f"Keyword Density para {text!r}: esperado {expected}, actual {actual}"
