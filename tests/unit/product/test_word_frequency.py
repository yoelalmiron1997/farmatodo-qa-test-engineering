"""Ejercicio 4 — algoritmo de frecuencia de palabras (TC-ALG-001…011)."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from farmatodo_qa.word_frequency import analyze, count_characters, render_histogram, render_report
from farmatodo_qa.word_frequency.cli import EXIT_DECODE_ERROR, EXIT_FILE_ERROR, main

ROOT = Path(__file__).resolve().parents[3]
EXAMPLE = ROOT / "data" / "samples" / "farmatodo_example.txt"
GOLDEN = "14 words\n99 characters\nfarmatodo: 6\ncuida: 3\nsalud: 2\ntu: 2\ntoda: 1\n"


@pytest.mark.case("TC-ALG-001")
def test_pdf_example_output_matches_golden_byte_for_byte(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([str(EXAMPLE)]) == 0
    assert capsys.readouterr().out == GOLDEN


@pytest.mark.case("TC-ALG-002")
@pytest.mark.parametrize(
    ("text", "expected"),
    [("a b  c", 3), ("", 0), ("\n\n", 0), ("uno\ndos", 2)],
    ids=["separadores-multiples", "vacio", "solo-saltos", "dos-lineas"],
)
def test_word_count(text: str, expected: int) -> None:
    assert analyze(text).words == expected, f"texto={text!r}"


@pytest.mark.case("TC-ALG-003")
@pytest.mark.parametrize(
    ("text", "expected"),
    [("ab\ncd", 4), ("ab\r\ncd", 4), ("a b", 3), ("a\tb", 3), ("abc\n", 3)],
    ids=["lf", "crlf", "espacio", "tab", "salto-final"],
)
def test_character_count_excludes_line_breaks(text: str, expected: int) -> None:
    assert count_characters(text) == expected
    assert analyze(text).characters == expected


@pytest.mark.case("TC-ALG-004")
@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("b a b a c", (("a", 2), ("b", 2), ("c", 1))),
        ("z y y x x x", (("x", 3), ("y", 2), ("z", 1))),
    ],
    ids=["empate-alfabetico", "descendente"],
)
def test_sorted_by_frequency_then_alphabetically(text: str, expected: tuple[tuple[str, int], ...]) -> None:
    assert analyze(text).frequencies == expected


@pytest.mark.case("TC-ALG-005")
@pytest.mark.parametrize("content", ["", "\n\n\n"], ids=["vacio", "solo-saltos"])
def test_empty_file(tmp_path: Path, content: str, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "empty.txt"
    path.write_text(content, encoding="utf-8")
    assert main([str(path)]) == 0
    assert capsys.readouterr().out == "0 words\n0 characters\n"


@pytest.mark.case("TC-ALG-006")
def test_missing_file_reports_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main([str(tmp_path / "no-existe.txt")]) == EXIT_FILE_ERROR
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "no se puede leer" in captured.err
    assert "Traceback" not in captured.err


@pytest.mark.case("TC-ALG-006")
def test_invalid_utf8_reports_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "latin1.txt"
    path.write_bytes("acción".encode("latin-1"))
    assert main([str(path)]) == EXIT_DECODE_ERROR
    assert "UTF-8" in capsys.readouterr().err


@pytest.mark.case("TC-ALG-006")
def test_utf8_bom_is_not_counted(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "bom.txt"
    path.write_bytes(b"\xef\xbb\xbfhola mundo")
    assert main([str(path)]) == 0
    assert capsys.readouterr().out.splitlines()[:2] == ["2 words", "10 characters"]


@pytest.mark.case("TC-ALG-007")
def test_punctuation_and_case_are_normalized() -> None:
    stats = analyze("Hola, hola. HOLA!")
    assert (stats.words, stats.characters, stats.frequencies) == (3, 17, (("hola", 3),))


@pytest.mark.case("TC-ALG-008")
def test_unicode_words_are_not_split() -> None:
    assert analyze("Niño niño ÁRBOL árbol").frequencies == (("niño", 2), ("árbol", 2))


@pytest.mark.case("TC-ALG-008")
def test_nfc_and_nfd_forms_are_unified() -> None:
    assert analyze("camión camión").frequencies == (("camión", 2),)


@pytest.mark.case("TC-ALG-009")
def test_histogram_is_proportional_and_keeps_order() -> None:
    frequencies = analyze(EXAMPLE.read_text(encoding="utf-8")).frequencies
    expected = (
        "farmatodo | ██████████████████████████████ 6\n"
        "cuida     | ███████████████ 3\n"
        "salud     | ██████████ 2\n"
        "tu        | ██████████ 2\n"
        "toda      | █████ 1\n"
    )
    assert render_histogram(frequencies, width=30) == expected


@pytest.mark.case("TC-ALG-009")
def test_histogram_flag_appends_bars(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([str(EXAMPLE), "--histogram", "--width", "6"]) == 0
    out = capsys.readouterr().out
    assert out.startswith(GOLDEN)
    assert "farmatodo | ██████ 6" in out


@pytest.mark.case("TC-ALG-009")
def test_report_uses_singular_for_one() -> None:
    assert render_report(analyze("hola")) == "1 word\n4 characters\nhola: 1\n"


@pytest.mark.case("TC-ALG-010")
def test_scaling_is_roughly_linear() -> None:
    vocabulary = [f"palabra{i}" for i in range(500)]

    def build(n: int) -> str:
        return " ".join(vocabulary[i % 500] for i in range(n))

    def median_time(text: str) -> float:
        samples = []
        for _ in range(3):
            start = time.perf_counter()
            analyze(text)
            samples.append(time.perf_counter() - start)
        return sorted(samples)[1]

    small, large = median_time(build(100_000)), median_time(build(200_000))
    # Informativo: solo falla ante una señal clara de complejidad cuadrática.
    assert large / small < 4, f"razón de tiempos {large / small:.2f}"


@pytest.mark.case("TC-ALG-011")
@pytest.mark.parametrize("text", ["uno\tdos", "uno dos", "uno     dos"], ids=["tab", "nbsp", "espacios"])
def test_whitespace_variants_separate_words(text: str) -> None:
    assert analyze(text).words == 2
