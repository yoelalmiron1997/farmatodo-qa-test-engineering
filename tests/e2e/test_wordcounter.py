"""Ejercicio 1 — wordcounter.net con Selenium (TC-WC-001…016).

Cada test usa su propio navegador y perfil (fixture ``wordcounter``, scope function), datos
explícitos y el oráculo como única fuente del valor esperado.
"""

from __future__ import annotations

import random
from pathlib import Path

import pytest

from farmatodo_qa.config import Settings
from farmatodo_qa.oracles import TextOracle
from farmatodo_qa.ui.pages import WordCounterPage
from farmatodo_qa.ui.waits import poll_until
from support.assertions import assert_all_keywords, assert_characters, assert_top_keywords, assert_words

pytestmark = [pytest.mark.e2e]

ROOT = Path(__file__).resolve().parents[2]
PDF_TEXT = (ROOT / "data/samples/farmatodo_example.txt").read_text(encoding="utf-8").rstrip("\n")
BASIC = {
    "pangrama-en": "the quick brown fox jumps over the lazy dog",
    "frase-es": "farmatodo cuida tu salud todos los dias",
    "una-palabra": "salud",
}


@pytest.mark.case("TC-WC-001")
@pytest.mark.parametrize("text", BASIC.values(), ids=BASIC.keys())
def test_basic_word_count(
    wordcounter: WordCounterPage, oracle: TextOracle, qa_settings: Settings, text: str
) -> None:
    wordcounter.type_text(text)
    assert_words(wordcounter, oracle, text, qa_settings.timeout_s)


@pytest.mark.case("TC-WC-002")
@pytest.mark.parametrize("text", BASIC.values(), ids=BASIC.keys())
def test_basic_character_count(
    wordcounter: WordCounterPage, oracle: TextOracle, qa_settings: Settings, text: str
) -> None:
    wordcounter.type_text(text)
    assert_characters(wordcounter, oracle, text, qa_settings.timeout_s)


@pytest.mark.case("TC-WC-003")
@pytest.mark.parametrize(
    "text",
    [
        "naranja naranja naranja naranja naranja limon limon limon pera pera kiwi",
        "pera naranja limon naranja pera naranja limon naranja kiwi naranja limon",
    ],
    ids=["agrupado", "intercalado"],
)
def test_top_three_keywords(
    wordcounter: WordCounterPage, oracle: TextOracle, qa_settings: Settings, text: str
) -> None:
    assert [str(k) for k in oracle.top_keywords(text)] == [
        "naranja=5",
        "limon=3",
        "pera=2",
    ]  # datos sin empates
    wordcounter.type_text(text)
    assert_top_keywords(wordcounter, oracle, text, qa_settings.timeout_s)


@pytest.mark.case("TC-WC-004")
def test_pdf_example_text(wordcounter: WordCounterPage, oracle: TextOracle, qa_settings: Settings) -> None:
    wordcounter.type_text(PDF_TEXT)
    assert_words(wordcounter, oracle, PDF_TEXT, qa_settings.timeout_s)
    assert_characters(wordcounter, oracle, PDF_TEXT, qa_settings.timeout_s)
    assert_top_keywords(wordcounter, oracle, PDF_TEXT, qa_settings.timeout_s)


@pytest.mark.case("TC-WC-005")
@pytest.mark.parametrize(
    "text", ["  hola   mundo  ", "hola  mundo"], ids=["bordes-y-multiples", "doble-espacio"]
)
def test_extra_spaces(
    wordcounter: WordCounterPage, oracle: TextOracle, qa_settings: Settings, text: str
) -> None:
    wordcounter.type_text(text)
    assert_words(wordcounter, oracle, text, qa_settings.timeout_s)
    assert_characters(wordcounter, oracle, text, qa_settings.timeout_s)


@pytest.mark.case("TC-WC-006")
@pytest.mark.parametrize(
    "text", ["Hola, mundo. Hola; mundo! (hola)", "hola - mundo"], ids=["puntuacion", "guion-aislado"]
)
def test_punctuation(
    wordcounter: WordCounterPage, oracle: TextOracle, qa_settings: Settings, text: str
) -> None:
    wordcounter.type_text(text)
    assert_words(wordcounter, oracle, text, qa_settings.timeout_s)
    assert_all_keywords(wordcounter, oracle, text, qa_settings.timeout_s)


@pytest.mark.case("TC-WC-007")
def test_keyword_density_is_case_insensitive(
    wordcounter: WordCounterPage, oracle: TextOracle, qa_settings: Settings
) -> None:
    text = "Salud salud SALUD bienestar Bienestar vida"
    wordcounter.type_text(text)
    assert_top_keywords(wordcounter, oracle, text, qa_settings.timeout_s)


@pytest.mark.case("TC-WC-008")
def test_counters_follow_content_updates(
    wordcounter: WordCounterPage, oracle: TextOracle, qa_settings: Settings
) -> None:
    timeout = qa_settings.timeout_s
    wordcounter.type_text("uno dos tres")
    assert_words(wordcounter, oracle, "uno dos tres", timeout)

    wordcounter.type_text("alfa alfa beta")  # reemplazo completo
    assert_words(wordcounter, oracle, "alfa alfa beta", timeout)
    assert_characters(wordcounter, oracle, "alfa alfa beta", timeout)
    assert_all_keywords(wordcounter, oracle, "alfa alfa beta", timeout)

    wordcounter.append_text(" gamma")
    assert_words(wordcounter, oracle, "alfa alfa beta gamma", timeout)
    assert_all_keywords(wordcounter, oracle, "alfa alfa beta gamma", timeout)


@pytest.mark.case("TC-WC-009")
def test_clearing_text_resets_counters(
    wordcounter: WordCounterPage, oracle: TextOracle, qa_settings: Settings
) -> None:
    wordcounter.type_text("uno dos tres")
    assert_words(wordcounter, oracle, "uno dos tres", qa_settings.timeout_s)
    wordcounter.clear()
    assert_words(wordcounter, oracle, "", qa_settings.timeout_s)
    assert_characters(wordcounter, oracle, "", qa_settings.timeout_s)
    keywords = poll_until(wordcounter.keyword_density.keywords, lambda v: v == [], qa_settings.timeout_s)
    assert keywords == [], f"Keyword Density debería quedar vacía; actual {keywords}"


@pytest.mark.case("TC-WC-010")
def test_multiline_text(wordcounter: WordCounterPage, oracle: TextOracle, qa_settings: Settings) -> None:
    text = "linea uno\nlinea dos\nlinea tres"
    wordcounter.type_text(text)
    assert_words(wordcounter, oracle, text, qa_settings.timeout_s)
    assert_characters(wordcounter, oracle, text, qa_settings.timeout_s)
    assert_top_keywords(wordcounter, oracle, text, qa_settings.timeout_s)


@pytest.mark.case("TC-WC-011")
def test_ties_are_ordered_by_first_appearance(
    wordcounter: WordCounterPage, oracle: TextOracle, qa_settings: Settings
) -> None:
    text = "beta beta alfa alfa gamma gamma delta"
    wordcounter.type_text(text)
    assert_top_keywords(wordcounter, oracle, text, qa_settings.timeout_s)


@pytest.mark.case("TC-WC-012")
def test_spanish_accents(wordcounter: WordCounterPage, oracle: TextOracle, qa_settings: Settings) -> None:
    text = "niño niño camión camión camión acción"
    wordcounter.type_text(text)
    assert_words(wordcounter, oracle, text, qa_settings.timeout_s)
    assert_characters(wordcounter, oracle, text, qa_settings.timeout_s)
    assert_top_keywords(wordcounter, oracle, text, qa_settings.timeout_s)


@pytest.mark.case("TC-WC-013")
def test_numbers_hyphens_and_apostrophes(
    wordcounter: WordCounterPage, oracle: TextOracle, qa_settings: Settings
) -> None:
    text = "e-commerce 2026 don't 3.5 x-ray"
    wordcounter.type_text(text)
    assert_words(wordcounter, oracle, text, qa_settings.timeout_s)


@pytest.mark.case("TC-WC-014")
def test_long_text(wordcounter: WordCounterPage, oracle: TextOracle, qa_settings: Settings) -> None:
    vocabulary = [
        f"{w}{s}" for w in ("salud", "farmacia", "cuidado", "vitamina", "receta") for s in "abcdefghij"
    ]
    rng = random.Random(20261023)  # semilla fija: dato reproducible
    text = " ".join(rng.choice(vocabulary) for _ in range(2000))
    wordcounter.set_text_via_script(text)  # send_keys de 2.000 palabras es lento; el sitio recalcula en keyup
    timeout = qa_settings.timeout_s * 2
    assert_words(wordcounter, oracle, text, timeout)
    assert_characters(wordcounter, oracle, text, timeout)
    assert_top_keywords(wordcounter, oracle, text, timeout)


@pytest.mark.case("TC-WC-015")
@pytest.mark.parametrize(
    "text",
    ["the the the and and data data data data", "b c d", "1,000 2.000"],
    ids=["stop-words", "una-letra", "numeros"],
)
def test_keyword_density_default_filters(
    wordcounter: WordCounterPage, oracle: TextOracle, qa_settings: Settings, text: str
) -> None:
    wordcounter.type_text(text)
    assert_words(wordcounter, oracle, text, qa_settings.timeout_s)
    assert_all_keywords(wordcounter, oracle, text, qa_settings.timeout_s)


@pytest.mark.case("TC-WC-016")
def test_emoji_character_count_characterization(
    wordcounter: WordCounterPage, oracle: TextOracle, qa_settings: Settings
) -> None:
    text = "hola 👋 mundo 🌎"
    wordcounter.set_text_via_script(text)  # ChromeDriver no tipea caracteres fuera del BMP
    assert_words(wordcounter, oracle, text, qa_settings.timeout_s)
    assert_characters(wordcounter, oracle, text, qa_settings.timeout_s)  # perfil UTF-16 (ver BUG-WC-004)
