"""Reporte resumen exigido por el PDF (TC-RPT-001)."""

from __future__ import annotations

import pytest

from farmatodo_qa.quality_gate import default_policy, evaluate
from farmatodo_qa.reporting.summary import render_html, render_markdown
from support.factories import O, case, run


def synthetic_run():  # type: ignore[no-untyped-def]
    cases = [
        case("TC-WC-001", (O.PASSED,), title="Conteo básico de palabras"),
        case("TC-WC-002", (O.PASSED,)),
        case("TC-WC-003", (O.PASSED,)),
        case("TC-WC-004", (O.FAILED, O.PASSED), priority="P1"),
        case("TC-WC-005", (O.FAILED, O.FAILED, O.FAILED), priority="P1", title="Espacios adicionales"),
        case("TC-WC-006", (O.FAILED, O.FAILED, O.FAILED), priority="P2"),
        case("TC-WC-007", (O.SKIPPED,), priority="P2"),
        case("TC-WC-008", (O.BLOCKED,), priority="P2"),
    ]
    r = run(cases)
    return r.model_copy(update={"gate": evaluate(r, default_policy())})


@pytest.mark.case("TC-RPT-001")
def test_markdown_summary_has_totals_and_error_descriptions() -> None:
    md = render_markdown(synthetic_run())
    assert "| Escenarios (tests) | 6 | 3 | 1 | 2 | 1 | 1 | — |" in md
    assert "| Casos especificados | 6 | 3 | 1 | 2 | 1 | 1 | 0 |" in md
    assert "TC-WC-005 — Espacios adicionales" in md
    assert "esperado 9, actual 8" in md
    assert "evidence/a1.png" in md
    assert "Quality gate:** BLOCK" in md
    assert "sitio inaccesible" in md  # motivo del BLOCKED


@pytest.mark.case("TC-RPT-001")
def test_flaky_is_listed_apart_from_passed() -> None:
    md = render_markdown(synthetic_run())
    assert "FLAKY (falló y luego pasó)" in md
    assert "Un FLAKY nunca se suma a los aprobados" in md


@pytest.mark.case("TC-RPT-001")
def test_html_summary_escapes_and_lists_failures() -> None:
    r = synthetic_run()
    page = render_html(r)
    assert "Escenarios ejecutados: <strong>6</strong>" in page
    assert "Fallidos: <strong>2</strong>" in page
    assert page.count("<tr><td>TC-WC-00") == 3  # 2 FAIL + 1 FLAKY


@pytest.mark.case("TC-RPT-001")
def test_run_without_failures_says_so() -> None:
    md = render_markdown(run([case("TC-WC-001", (O.PASSED,))]))
    assert "Sin fallos en esta corrida." in md
