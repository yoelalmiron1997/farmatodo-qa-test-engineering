"""Page Object de WordCounter: operaciones de negocio, sin aserciones ni cálculos de esperados."""

from __future__ import annotations

import re
from dataclasses import dataclass

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from farmatodo_qa.oracles.wordcounter_oracle import Keyword
from farmatodo_qa.ui.pages import locators

_HEADLINE_RE = re.compile(r"(\d[\d,]*)\s+words?\s+(\d[\d,]*)\s+characters?", re.IGNORECASE)
_BADGE_RE = re.compile(r"(\d[\d,]*)")

# El sitio recalcula en `keyup` (no en `input`): comprobado en el spike del 2026-10-23.
_SET_TEXT_JS = """
const box = arguments[0];
box.value = arguments[1];
box.dispatchEvent(new KeyboardEvent('keyup', {bubbles: true}));
"""


@dataclass(frozen=True, slots=True)
class Counts:
    words: int
    characters: int


def _to_int(text: str) -> int:
    match = _BADGE_RE.search(text)
    if not match:
        raise ValueError(f"no se encontró un número en {text!r}")
    return int(match.group(1).replace(",", ""))


class KeywordDensityPanel:
    def __init__(self, driver: WebDriver) -> None:
        self._driver = driver

    def keywords(self) -> list[Keyword]:
        result = []
        for row in self._driver.find_elements(*locators.KEYWORD_ROWS):
            word = row.find_element(*locators.KEYWORD_WORD).get_attribute("textContent") or ""
            badge = row.find_element(*locators.KEYWORD_BADGE).get_attribute("textContent") or ""
            result.append(Keyword(word.strip(), _to_int(badge)))
        return result

    def top(self, n: int = 3) -> list[Keyword]:
        return self.keywords()[:n]


class WordCounterPage:
    def __init__(self, driver: WebDriver, base_url: str, timeout_s: float) -> None:
        self._driver = driver
        self._base_url = base_url
        self._wait = WebDriverWait(driver, timeout_s)
        self.keyword_density = KeywordDensityPanel(driver)

    # ------------------------------------------------------------------ navegación
    def open(self) -> WordCounterPage:
        self._driver.get(self._base_url)
        self.editor()
        return self

    def editor(self) -> WebElement:
        element: WebElement = self._wait.until(ec.element_to_be_clickable(locators.EDITOR))
        return element

    # ------------------------------------------------------------------ entrada
    def clear(self) -> None:
        editor = self.editor()
        editor.click()
        editor.send_keys(Keys.CONTROL, "a")
        editor.send_keys(Keys.DELETE)

    def type_text(self, text: str) -> None:
        """Tipeo real con eventos nativos (por defecto)."""
        self.clear()
        if text:
            self.editor().send_keys(text)

    def append_text(self, text: str) -> None:
        editor = self.editor()
        editor.send_keys(Keys.END)
        editor.send_keys(text)

    def set_text_via_script(self, text: str) -> None:
        """Para textos largos o caracteres fuera del BMP, que ChromeDriver no puede tipear."""
        self._driver.execute_script(_SET_TEXT_JS, self.editor(), text)

    # ------------------------------------------------------------------ lectura
    def _text(self, locator: tuple[str, str]) -> str:
        return self._driver.find_element(*locator).get_attribute("textContent") or ""

    def counts(self) -> Counts:
        return Counts(
            words=_to_int(self._text(locators.WORD_COUNT)),
            characters=_to_int(self._text(locators.CHARACTER_COUNT)),
        )

    def headline_counts(self) -> Counts:
        text = self._text(locators.HEADLINE)
        match = _HEADLINE_RE.search(text)
        if not match:
            raise ValueError(f"encabezado inesperado: {text!r}")
        return Counts(int(match.group(1).replace(",", "")), int(match.group(2).replace(",", "")))

    def editor_value(self) -> str:
        return str(self._driver.execute_script("return arguments[0].value;", self.editor()))
