"""Fixtures aisladas: navegador y perfil nuevos por test (scope ``function``)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Callable, Generator
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from farmatodo_qa.config import Settings
from farmatodo_qa.oracles import WORDCOUNTER_PROFILE, TextOracle
from farmatodo_qa.pytest_plugin.blocked import block
from farmatodo_qa.pytest_plugin.collector import BROWSER_INFO_KEY, results_dir

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver

    from farmatodo_qa.ui.pages import WordCounterPage

_PROBE_TIMEOUT_S = 15
_USER_AGENT = "farmatodo-qa-probe/1.0 (+availability check before UI test)"


@pytest.fixture(scope="session")
def qa_settings() -> Settings:
    return Settings.from_env()


@pytest.fixture
def oracle() -> TextOracle:
    return TextOracle(WORDCOUNTER_PROFILE)


@pytest.fixture
def site_available(qa_settings: Settings) -> None:
    """Probe previo al test: DNS/TCP/TLS, 5xx o 429 ⇒ BLOCKED (nunca FAIL ni PASS)."""
    request = urllib.request.Request(qa_settings.base_url, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=_PROBE_TIMEOUT_S) as response:
            status = response.status
    except urllib.error.HTTPError as exc:
        status = exc.code
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        block(f"{qa_settings.base_url} inaccesible antes del test: {exc}")
    if status == 429 or status >= 500:
        block(f"{qa_settings.base_url} respondió HTTP {status} en el probe previo")


@pytest.fixture
def driver(
    request: pytest.FixtureRequest, qa_settings: Settings, tmp_path: Path, site_available: None
) -> Generator[WebDriver, None, None]:
    from farmatodo_qa.ui.browser import BrowserConfig, BrowserFactory, browser_versions

    config = BrowserConfig(
        name=qa_settings.browser,
        headless=qa_settings.headless,
        viewport=qa_settings.viewport,
        profile_dir=tmp_path / "browser-profile",
        version=qa_settings.browser_version,
    )
    web_driver = BrowserFactory().create(config)
    try:
        browser, driver_version = browser_versions(web_driver)
        request.config.stash[BROWSER_INFO_KEY] = {
            "name": qa_settings.browser,
            "version": browser,
            "driver_version": driver_version,
            "headless": qa_settings.headless,
            "viewport": qa_settings.viewport.replace(",", "x"),
        }
        yield web_driver
    finally:
        web_driver.quit()


@pytest.fixture
def wordcounter(driver: WebDriver, qa_settings: Settings) -> WordCounterPage:
    from selenium.common.exceptions import TimeoutException, WebDriverException

    from farmatodo_qa.ui.pages import WordCounterPage

    page = WordCounterPage(driver, qa_settings.base_url, qa_settings.timeout_s)
    try:
        page.open()
    except TimeoutException:
        block("el editor #box no estuvo disponible al cargar (posible interstitial o cambio del sitio)")
    except WebDriverException as exc:
        if "net::ERR_" in str(exc):
            block(f"error de red al navegar: {str(exc).splitlines()[0]}")
        raise
    return page


@pytest.fixture
def perf_recorder(request: pytest.FixtureRequest) -> Callable[..., None]:
    """Guarda series de performance en ``<results-dir>/performance.jsonl`` (separado de la medición)."""
    marker = request.node.get_closest_marker("case")
    case_id = str(marker.args[0]) if marker else None
    out_dir = results_dir(request.config)

    def record(series: str, samples: list[float], **meta: Any) -> None:
        if out_dir is None:
            return
        out_dir.mkdir(parents=True, exist_ok=True)
        entry = {"case_id": case_id, "series": series, "samples": [round(s, 2) for s in samples], **meta}
        with (out_dir / "performance.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return record
