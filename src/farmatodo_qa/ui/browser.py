"""Fábrica de navegadores con registro por nombre (OCP: agregar uno = registrar un builder)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver


@dataclass(frozen=True, slots=True)
class BrowserConfig:
    name: str
    headless: bool
    viewport: str
    profile_dir: Path  # perfil temporal nuevo por test: sin localStorage previo (autosave del sitio)
    language: str = "en-US"
    version: str | None = None  # None = navegador instalado; valor = versión exacta vía Selenium Manager


BrowserBuilder = Callable[[BrowserConfig], WebDriver]


def chrome_options(config: BrowserConfig) -> webdriver.ChromeOptions:
    options = webdriver.ChromeOptions()
    if config.version:
        options.browser_version = config.version
    if config.headless:
        options.add_argument("--headless=new")
    options.add_argument(f"--window-size={config.viewport}")
    options.add_argument(f"--user-data-dir={config.profile_dir}")
    options.add_argument(f"--lang={config.language}")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.set_capability("goog:loggingPrefs", {"browser": "SEVERE"})
    return options


def _chrome(config: BrowserConfig) -> WebDriver:
    return webdriver.Chrome(options=chrome_options(config))  # Selenium Manager resuelve el driver compatible


def _firefox(config: BrowserConfig) -> WebDriver:
    options = webdriver.FirefoxOptions()
    if config.version:
        options.browser_version = config.version
    if config.headless:
        options.add_argument("-headless")
    options.add_argument("-profile")
    options.add_argument(str(config.profile_dir))
    driver = webdriver.Firefox(options=options)
    width, height = (int(v) for v in config.viewport.split(","))
    driver.set_window_size(width, height)
    return driver


class BrowserFactory:
    def __init__(self) -> None:
        self._builders: dict[str, BrowserBuilder] = {"chrome": _chrome, "firefox": _firefox}

    def register(self, name: str, builder: BrowserBuilder) -> None:
        self._builders[name] = builder

    @property
    def available(self) -> tuple[str, ...]:
        return tuple(sorted(self._builders))

    def create(self, config: BrowserConfig) -> WebDriver:
        try:
            builder = self._builders[config.name]
        except KeyError as exc:
            raise ValueError(
                f"navegador no soportado: {config.name} (disponibles: {self.available})"
            ) from exc
        driver = builder(config)
        driver.implicitly_wait(0)  # solo esperas explícitas
        return driver


def browser_versions(driver: WebDriver) -> tuple[str | None, str | None]:
    caps = driver.capabilities
    browser = caps.get("browserVersion")
    driver_version = None
    chrome = caps.get("chrome")
    if isinstance(chrome, dict):
        driver_version = str(chrome.get("chromedriverVersion", "")).split(" ", 1)[0] or None
    return browser, driver_version
