"""Configuración inmutable y límites de cortesía de performance (TC-FW-005)."""

from __future__ import annotations

import dataclasses

import pytest

from farmatodo_qa.config import Settings


@pytest.mark.case("TC-FW-005")
def test_defaults_without_environment() -> None:
    settings = Settings.from_env({})
    assert (settings.base_url, settings.browser, settings.headless) == (
        "https://wordcounter.net/",
        "chrome",
        True,
    )
    assert (settings.perf_samples, settings.perf_warmup) == (5, 1)


@pytest.mark.case("TC-FW-005")
@pytest.mark.parametrize(("requested", "effective"), [("3", 3), ("10", 10), ("500", 10), ("0", 1)])
def test_performance_samples_are_capped(requested: str, effective: int) -> None:
    assert Settings.from_env({"QA_PERF_SAMPLES": requested}).perf_samples == effective


@pytest.mark.case("TC-FW-005")
@pytest.mark.parametrize(
    ("value", "expected"), [(None, None), ("", None), ("  ", None), ("155.0.8059.39", "155.0.8059.39")]
)
def test_browser_version_pin(value: str | None, expected: str | None) -> None:
    env = {} if value is None else {"QA_BROWSER_VERSION": value}
    assert Settings.from_env(env).browser_version == expected


@pytest.mark.case("TC-FW-005")
def test_settings_are_immutable() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        Settings().timeout_s = 1  # type: ignore[misc]
