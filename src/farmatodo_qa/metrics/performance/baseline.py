"""Baseline y alertas de cambio significativo (no son pruebas estadísticas de regresión).

* Baseline = mediana de las medianas de las primeras ``k`` corridas válidas del mismo entorno.
* Alerta si ``actual > baseline * (1 + relative)`` **y** ``actual - baseline > absolute_ms``.
"""

from __future__ import annotations

import statistics
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

DEFAULT_BASELINE_RUNS = 5
DEFAULT_RELATIVE = 0.5
DEFAULT_ABSOLUTE_MS = 200.0


class BaselineStatus(StrEnum):
    COLLECTING = "collecting_baseline"
    OK = "ok"
    ALERT = "alert"


@dataclass(frozen=True, slots=True)
class BaselineComparison:
    status: BaselineStatus
    baseline_ms: float | None
    current_ms: float | None
    delta_ms: float | None
    ratio: float | None


def compute_baseline(run_medians: Sequence[float], k: int = DEFAULT_BASELINE_RUNS) -> float | None:
    if len(run_medians) < k:
        return None
    return statistics.median(run_medians[:k])


def compare(
    current_median: float | None,
    baseline_ms: float | None,
    relative: float = DEFAULT_RELATIVE,
    absolute_ms: float = DEFAULT_ABSOLUTE_MS,
) -> BaselineComparison:
    if baseline_ms is None or current_median is None:
        return BaselineComparison(BaselineStatus.COLLECTING, baseline_ms, current_median, None, None)
    delta = current_median - baseline_ms
    ratio = current_median / baseline_ms if baseline_ms else None
    alert = current_median > baseline_ms * (1 + relative) and delta > absolute_ms
    return BaselineComparison(
        BaselineStatus.ALERT if alert else BaselineStatus.OK, baseline_ms, current_median, delta, ratio
    )
