"""Plugin de pytest (``-p farmatodo_qa.pytest_plugin``): recolección por intento y fixtures.

La escritura de resultados se activa con ``--qa-results-dir``. Las fixtures de navegador
importan Selenium solo al usarse, así la suite unitaria no lo necesita.
"""

from farmatodo_qa.pytest_plugin.collector import pytest_addoption, pytest_configure
from farmatodo_qa.pytest_plugin.fixtures import (
    driver,
    oracle,
    perf_recorder,
    qa_settings,
    site_available,
    wordcounter,
)

__all__ = [
    "driver",
    "oracle",
    "perf_recorder",
    "pytest_addoption",
    "pytest_configure",
    "qa_settings",
    "site_available",
    "wordcounter",
]
