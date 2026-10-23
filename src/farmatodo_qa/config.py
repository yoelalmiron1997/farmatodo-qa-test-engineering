"""Configuración inmutable construida una vez desde variables de entorno."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass


def _bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class Settings:
    base_url: str = "https://wordcounter.net/"
    browser: str = "chrome"
    headless: bool = True
    timeout_s: float = 10.0
    viewport: str = "1366,768"
    results_dir: str = "reports"
    perf_samples: int = 5
    perf_warmup: int = 1
    perf_max_samples: int = 10

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Settings:
        env = os.environ if env is None else env
        d = cls()  # valores por defecto
        samples = int(env.get("QA_PERF_SAMPLES", d.perf_samples))
        return cls(
            base_url=env.get("QA_BASE_URL", d.base_url),
            browser=env.get("QA_BROWSER", d.browser),
            headless=_bool(env.get("QA_HEADLESS"), d.headless),
            timeout_s=float(env.get("QA_TIMEOUT", d.timeout_s)),
            viewport=env.get("QA_VIEWPORT", d.viewport),
            results_dir=env.get("QA_RESULTS_DIR", d.results_dir),
            # Límite de cortesía con el sitio de terceros: nunca más de perf_max_samples.
            perf_samples=max(1, min(samples, d.perf_max_samples)),
            perf_warmup=max(0, int(env.get("QA_PERF_WARMUP", d.perf_warmup))),
        )
