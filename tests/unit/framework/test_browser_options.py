"""Fijar la versión del navegador para reproducir una ejecución (TC-FW-005). No abre navegadores."""

from __future__ import annotations

from pathlib import Path

import pytest

from farmatodo_qa.ui.browser import BrowserConfig, chrome_options


def _config(version: str | None) -> BrowserConfig:
    return BrowserConfig(
        name="chrome", headless=True, viewport="1366,768", profile_dir=Path("perfil"), version=version
    )


@pytest.mark.case("TC-FW-005")
def test_installed_browser_by_default() -> None:
    assert chrome_options(_config(None)).browser_version is None


@pytest.mark.case("TC-FW-005")
def test_exact_version_is_requested_to_selenium_manager() -> None:
    options = chrome_options(_config("155.0.8059.39"))
    assert options.browser_version == "155.0.8059.39"
    assert "--headless=new" in options.arguments
