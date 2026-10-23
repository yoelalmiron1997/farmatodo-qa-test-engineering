"""Estabilidad histórica y flaky sospechado (SDD Anexo C.3).

* Corridas comparables: mismo ``spec_hash`` del caso, mismo tipo de entorno y SO y misma
  versión mayor del navegador que la observación más reciente del caso.
* ``estabilidad = PASS limpios / n`` sobre las últimas ``window`` ejecuciones comparables.
* ``flip_rate = cambios de estado entre corridas consecutivas / (n - 1)``; FLAKY cuenta
  como estado distinto de PASS.
* Sospechado si ``n >= min_runs`` y (``flip_rate >= flip_threshold`` o ``>= 2`` FLAKY) y el
  caso no está fallando de forma consistente en las últimas ``consistent_fail_tail`` corridas.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime
from itertools import pairwise

from farmatodo_qa.results.models import EXECUTED_STATUSES, CaseResult, FinalStatus, RunResult


@dataclass(frozen=True, slots=True)
class HistoryPoint:
    run_key: str
    started_at: datetime
    commit_sha: str
    status: FinalStatus
    comparable_key: tuple[str, str, str, str]


@dataclass(frozen=True, slots=True)
class StabilityStats:
    case_id: str
    priority: str
    n: int
    clean_passes: int
    flaky_observed: int
    failures: int
    flips: int
    stability: float | None
    flip_rate: float | None
    suspected: bool
    timeline: tuple[HistoryPoint, ...]


def _browser_major(run: RunResult) -> str:
    browser = run.environment.browser
    if browser is None or not browser.version:
        return "-"
    return browser.version.split(".", 1)[0]


def _comparable_key(run: RunResult, case: CaseResult) -> tuple[str, str, str, str]:
    return (case.spec_hash, run.environment.kind, run.environment.os, _browser_major(run))


def case_timelines(runs: Iterable[RunResult]) -> dict[str, list[HistoryPoint]]:
    """Puntos ejecutados por caso, en orden cronológico."""
    timelines: dict[str, list[HistoryPoint]] = {}
    priorities: dict[str, str] = {}
    for run in sorted(runs, key=lambda r: r.run.started_at):
        for case in run.cases:
            if case.final_status not in EXECUTED_STATUSES:
                continue
            priorities[case.case_id] = case.priority
            timelines.setdefault(case.case_id, []).append(
                HistoryPoint(
                    run_key=run.key,
                    started_at=run.run.started_at,
                    commit_sha=run.run.commit_sha,
                    status=case.final_status,
                    comparable_key=_comparable_key(run, case),
                )
            )
    return timelines


def _stats_for(
    case_id: str,
    priority: str,
    points: Sequence[HistoryPoint],
    *,
    window: int,
    min_runs: int,
    flip_threshold: float,
    consistent_fail_tail: int,
) -> StabilityStats:
    reference = points[-1].comparable_key
    comparable = [p for p in points if p.comparable_key == reference][-window:]
    n = len(comparable)
    statuses = [p.status for p in comparable]
    clean = statuses.count(FinalStatus.PASS)
    flaky = statuses.count(FinalStatus.FLAKY)
    failures = statuses.count(FinalStatus.FAIL)
    flips = sum(1 for prev, curr in pairwise(statuses) if prev != curr)
    flip_rate = flips / (n - 1) if n > 1 else None
    tail = statuses[-consistent_fail_tail:]
    consistently_failing = len(tail) == consistent_fail_tail and all(s is FinalStatus.FAIL for s in tail)
    suspected = (
        n >= min_runs
        and not consistently_failing
        and ((flip_rate is not None and flip_rate >= flip_threshold) or flaky >= 2)
    )
    return StabilityStats(
        case_id=case_id,
        priority=priority,
        n=n,
        clean_passes=clean,
        flaky_observed=flaky,
        failures=failures,
        flips=flips,
        stability=clean / n if n else None,
        flip_rate=flip_rate,
        suspected=suspected,
        timeline=tuple(comparable),
    )


def analyze_stability(
    runs: Iterable[RunResult],
    window: int = 20,
    min_runs: int = 5,
    flip_threshold: float = 0.2,
    consistent_fail_tail: int = 3,
) -> dict[str, StabilityStats]:
    runs = list(runs)
    priorities = {case.case_id: case.priority for run in runs for case in run.cases}
    return {
        case_id: _stats_for(
            case_id,
            priorities[case_id],
            points,
            window=window,
            min_runs=min_runs,
            flip_threshold=flip_threshold,
            consistent_fail_tail=consistent_fail_tail,
        )
        for case_id, points in case_timelines(runs).items()
    }


def top_unstable(stats: Iterable[StabilityStats], k: int = 10, min_runs: int = 3) -> list[StabilityStats]:
    """Orden: (1 - estabilidad) desc, flip_rate desc, n desc. Excluye casos 100 % estables."""
    candidates = [s for s in stats if s.n >= min_runs and s.stability is not None and s.stability < 1]
    candidates.sort(key=lambda s: (-(1 - (s.stability or 0)), -(s.flip_rate or 0), -s.n, s.case_id))
    return candidates[:k]
