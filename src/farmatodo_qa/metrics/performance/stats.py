"""Estadística descriptiva con advertencias explícitas de robustez."""

from __future__ import annotations

import math
import statistics
from collections.abc import Sequence
from dataclasses import dataclass

MIN_SAMPLES_STDEV = 3
MIN_SAMPLES_P95 = 20


@dataclass(frozen=True, slots=True)
class PerfStats:
    n: int
    minimum: float | None
    mean: float | None
    median: float | None
    maximum: float | None
    stdev: float | None
    p95: float | None
    warnings: tuple[str, ...]


def _nearest_rank(sorted_samples: Sequence[float], percentile: float) -> float:
    rank = max(1, math.ceil(percentile / 100 * len(sorted_samples)))
    return sorted_samples[rank - 1]


def describe(samples: Sequence[float]) -> PerfStats:
    n = len(samples)
    if n == 0:
        return PerfStats(0, None, None, None, None, None, None, ("sin muestras",))
    ordered = sorted(samples)
    warnings: list[str] = []
    stdev = statistics.stdev(ordered) if n >= MIN_SAMPLES_STDEV else None
    if stdev is None:
        warnings.append(f"desvío no calculado: n < {MIN_SAMPLES_STDEV}")
    p95 = _nearest_rank(ordered, 95) if n >= MIN_SAMPLES_P95 else None
    if p95 is None:
        warnings.append(f"P95 no disponible: muestra insuficiente (n = {n} < {MIN_SAMPLES_P95})")
    return PerfStats(
        n=n,
        minimum=ordered[0],
        mean=statistics.fmean(ordered),
        median=statistics.median(ordered),
        maximum=ordered[-1],
        stdev=stdev,
        p95=p95,
        warnings=tuple(warnings),
    )
