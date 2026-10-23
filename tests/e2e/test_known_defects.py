"""Reproducción de defectos confirmados en el Ejercicio 2 (TC-WC-017…020).

Afirman el comportamiento **correcto**: fallan mientras el defecto exista (el gate los
muestra como "FAIL por defecto conocido", visible) y pasarán cuando se corrija, lo que
indica que hay que reverificar y cerrar el reporte.
"""

from __future__ import annotations

import pytest

from farmatodo_qa.config import Settings
from farmatodo_qa.oracles import CODEPOINT_CHARACTERS, TextOracle
from farmatodo_qa.ui.pages import WordCounterPage
from farmatodo_qa.ui.waits import poll_until
from support.assertions import assert_all_keywords, assert_characters

# `flaky(reruns=0)` es el marker de pytest-rerunfailures para desactivar reintentos en estos tests:
# su fallo es esperado y determinista, reintentarlo solo inflaría la métrica de reintentos.
pytestmark = [pytest.mark.e2e, pytest.mark.flaky(reruns=0)]


@pytest.mark.case("TC-WC-017")
@pytest.mark.known_defect("BUG-WC-001")
def test_word_count_and_keyword_density_agree_on_dot_without_space(
    wordcounter: WordCounterPage, qa_settings: Settings
) -> None:
    wordcounter.type_text("hola.mundo")
    keywords = poll_until(wordcounter.keyword_density.keywords, lambda v: len(v) > 0, qa_settings.timeout_s)
    words = wordcounter.counts().words
    keyword_total = sum(k.count for k in keywords)
    assert words == keyword_total, (
        f"Inconsistencia: el contador muestra {words} palabra(s) y Keyword Density suma {keyword_total} "
        f"({[str(k) for k in keywords]}) para 'hola.mundo'"
    )


@pytest.mark.case("TC-WC-018")
@pytest.mark.known_defect("BUG-WC-002")
def test_hyphen_only_token_is_not_a_keyword(
    wordcounter: WordCounterPage, oracle: TextOracle, qa_settings: Settings
) -> None:
    wordcounter.type_text("---")
    characters = poll_until(lambda: wordcounter.counts().characters, lambda v: v == 3, qa_settings.timeout_s)
    assert characters == 3, f"el texto no se cargó: caracteres {characters}"
    assert wordcounter.counts().words == 0, "el contador debería indicar 0 palabras para '---'"
    assert_all_keywords(wordcounter, oracle, "---", qa_settings.timeout_s)


@pytest.mark.case("TC-WC-019")
@pytest.mark.known_defect("BUG-WC-003")
def test_keyword_density_splits_on_non_breaking_space(
    wordcounter: WordCounterPage, oracle: TextOracle, qa_settings: Settings
) -> None:
    text = "uno dos"
    wordcounter.set_text_via_script(text)
    assert_all_keywords(wordcounter, oracle, text, qa_settings.timeout_s)


@pytest.mark.case("TC-WC-020")
@pytest.mark.known_defect("BUG-WC-004")
def test_each_emoji_counts_as_one_character(wordcounter: WordCounterPage, qa_settings: Settings) -> None:
    text = "hola 👋 mundo 🌎"
    wordcounter.set_text_via_script(text)
    assert_characters(wordcounter, TextOracle(CODEPOINT_CHARACTERS), text, qa_settings.timeout_s)
