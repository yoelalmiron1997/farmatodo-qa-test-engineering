"""Mediciones ligeras de performance — P2 (TC-PERF-001…003).

Reglas de cortesía: secuencial, sin concurrencia, muestras limitadas (máx. 10), pausa entre
muestras **fuera** del intervalo medido. Medición, validación y registro están separados;
la estadística y el baseline se calculan después, en el núcleo (``metrics.performance``).
"""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from farmatodo_qa.config import Settings
from farmatodo_qa.oracles import TextOracle
from farmatodo_qa.ui.browser import BrowserConfig, BrowserFactory
from farmatodo_qa.ui.pages import WordCounterPage
from farmatodo_qa.ui.waits import poll_until

pytestmark = [pytest.mark.performance]

COURTESY_PAUSE_S = 2.0
POLL_S = 0.025

_NAVIGATION_JS = """
const n = performance.getEntriesByType('navigation')[0];
return n ? {ttfb: n.responseStart, dcl: n.domContentLoadedEventEnd, load: n.loadEventEnd} : null;
"""

# Mide dentro del navegador: desde el keyup hasta que el nodo observado muestra el valor esperado.
_OBSERVE_AND_SET_JS = """
const [selector, text, expected, mode] = arguments;
const read = () => {
  if (mode === 'keywords') {
    return [...document.querySelectorAll('#kwd-accordion-data a.list-group-item')].slice(0, 3)
      .map(r => r.querySelector('.word').textContent.trim() + '=' + parseInt(r.querySelector('.badge').textContent, 10))
      .join('|');
  }
  return document.querySelector(selector).textContent.trim();
};
window.__qa = {t0: null, t1: null};
const target = document.querySelector(selector);
const observer = new MutationObserver(() => {
  if (window.__qa.t1 === null && read() === expected) { window.__qa.t1 = performance.now(); observer.disconnect(); }
});
observer.observe(target, {childList: true, characterData: true, subtree: true});
const box = document.getElementById('box');
window.__qa.t0 = performance.now();
box.value = text;
box.dispatchEvent(new KeyboardEvent('keyup', {bubbles: true}));
if (read() === expected && window.__qa.t1 === null) { window.__qa.t1 = performance.now(); observer.disconnect(); }
"""


def _samples_plan(settings: Settings) -> list[bool]:
    """True = muestra registrada; False = calentamiento descartado."""
    return [False] * settings.perf_warmup + [True] * settings.perf_samples


@pytest.mark.case("TC-PERF-001")
def test_navigation_timing(
    qa_settings: Settings, site_available: None, tmp_path: Path, perf_recorder: Callable[..., None]
) -> None:
    series: dict[str, list[float]] = {
        "navigation_ttfb": [],
        "navigation_dcl": [],
        "navigation_load": [],
        "editor_ready": [],
    }
    invalid = 0
    factory = BrowserFactory()
    for index, recorded in enumerate(_samples_plan(qa_settings)):
        config = BrowserConfig(
            qa_settings.browser, qa_settings.headless, qa_settings.viewport, tmp_path / f"p{index}"
        )
        driver = factory.create(config)  # perfil nuevo por muestra: sin caché ni localStorage
        try:
            page = WordCounterPage(driver, qa_settings.base_url, qa_settings.timeout_s)
            start = time.perf_counter()
            page.open()
            editor_ready_ms = (time.perf_counter() - start) * 1000
            timing = driver.execute_script(_NAVIGATION_JS)
        finally:
            driver.quit()
        if recorded:
            if not timing or not timing.get("load"):
                invalid += 1
            else:
                series["navigation_ttfb"].append(timing["ttfb"])
                series["navigation_dcl"].append(timing["dcl"])
                series["navigation_load"].append(timing["load"])
                series["editor_ready"].append(editor_ready_ms)
        time.sleep(COURTESY_PAUSE_S)  # fuera del intervalo medido
    for name, samples in series.items():
        perf_recorder(name, samples, invalid_samples=invalid, warmup_discarded=qa_settings.perf_warmup)
    assert series["navigation_load"], "no se obtuvo ninguna medición válida de Navigation Timing"


def _measure_update(
    driver: WebDriver,
    settings: Settings,
    *,
    texts: tuple[str, str],
    selector: str,
    expected_of: Callable[[str], str],
    read_actual: Callable[[], str],
    mode: str,
) -> tuple[list[float], list[float], int]:
    end_to_end: list[float] = []
    in_browser: list[float] = []
    invalid = 0
    for index, recorded in enumerate(_samples_plan(settings)):
        text = texts[index % 2]  # alternar garantiza que siempre haya un cambio que recalcular
        expected = expected_of(text)
        start = time.perf_counter()
        driver.execute_script(_OBSERVE_AND_SET_JS, selector, text, expected, mode)
        actual = poll_until(read_actual, lambda v, e=expected: v == e, settings.timeout_s, interval_s=POLL_S)
        elapsed_ms = (time.perf_counter() - start) * 1000
        marks = driver.execute_script("return window.__qa;")
        if not recorded:
            continue
        if actual != expected or not marks or marks.get("t1") is None:
            invalid += 1  # una muestra con valor incorrecto no es una medición de performance válida
            continue
        end_to_end.append(elapsed_ms)
        in_browser.append(marks["t1"] - marks["t0"])
    return end_to_end, in_browser, invalid


@pytest.mark.case("TC-PERF-002")
def test_counter_update_latency(
    driver: WebDriver,
    wordcounter: WordCounterPage,
    oracle: TextOracle,
    qa_settings: Settings,
    perf_recorder: Callable[..., None],
) -> None:
    texts = (" ".join(["salud"] * 50), " ".join(["vida"] * 49))
    e2e, browser, invalid = _measure_update(
        driver,
        qa_settings,
        texts=texts,
        selector="#word_count",
        expected_of=lambda t: str(oracle.word_count(t)),
        read_actual=lambda: str(wordcounter.counts().words),
        mode="counter",
    )
    meta = {"invalid_samples": invalid, "warmup_discarded": qa_settings.perf_warmup}
    perf_recorder("end_to_end", e2e, poll_resolution_ms=POLL_S * 1000, **meta)
    perf_recorder("in_browser", browser, **meta)
    assert e2e, f"sin muestras válidas ({invalid} inválidas)"


@pytest.mark.case("TC-PERF-003")
def test_keyword_density_update_latency(
    driver: WebDriver,
    wordcounter: WordCounterPage,
    oracle: TextOracle,
    qa_settings: Settings,
    perf_recorder: Callable[..., None],
) -> None:
    texts = (
        "naranja naranja naranja naranja naranja limon limon limon pera pera kiwi",
        "manzana manzana manzana manzana uva uva uva melon melon kiwi",
    )

    def expected_of(text: str) -> str:
        return "|".join(str(k) for k in oracle.top_keywords(text))

    e2e, browser, invalid = _measure_update(
        driver,
        qa_settings,
        texts=texts,
        selector="#kwd-accordion-data",
        expected_of=expected_of,
        read_actual=lambda: "|".join(str(k) for k in wordcounter.keyword_density.top(3)),
        mode="keywords",
    )
    meta = {"invalid_samples": invalid, "warmup_discarded": qa_settings.perf_warmup}
    perf_recorder("end_to_end", e2e, poll_resolution_ms=POLL_S * 1000, **meta)
    perf_recorder("in_browser", browser, **meta)
    assert e2e, f"sin muestras válidas ({invalid} inválidas)"
