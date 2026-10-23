"""View-model del portal: agrega historial + especificaciones sin I/O.

Si no hay corridas, los indicadores quedan en ``None`` y el portal muestra "sin datos";
nunca se completan con ceros ni valores inventados.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime

from farmatodo_qa.metrics.flaky.history_analysis import StabilityStats, analyze_stability, top_unstable
from farmatodo_qa.metrics.performance.baseline import BaselineComparison, compare, compute_baseline
from farmatodo_qa.metrics.performance.stats import PerfStats, describe
from farmatodo_qa.results.models import FinalStatus, RunResult


@dataclass(frozen=True, slots=True)
class TrendPoint:
    run_key: str
    started_at: datetime
    commit_sha: str
    run_url: str | None
    executed: int
    passed: int
    flaky: int
    failed: int
    blocked: int
    skipped: int
    not_run: int
    retries: int
    gate: str


@dataclass(frozen=True, slots=True)
class CaseRunView:
    run_key: str
    started_at: datetime
    commit_sha: str
    run_url: str | None
    status: FinalStatus
    attempts: int
    messages: tuple[str, ...]
    evidence: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PerfSeriesView:
    case_id: str
    series: str
    latest: PerfStats
    latest_run_key: str
    environment: str
    comparison: BaselineComparison
    history: tuple[tuple[datetime, float], ...]


@dataclass(frozen=True, slots=True)
class DashboardModel:
    generated_at: datetime
    has_functional_data: bool
    has_performance_data: bool
    latest_functional: RunResult | None
    latest_performance: RunResult | None
    trend: tuple[TrendPoint, ...]
    stability: dict[str, StabilityStats]
    top_unstable: tuple[StabilityStats, ...]
    case_history: dict[str, tuple[CaseRunView, ...]]
    performance: tuple[PerfSeriesView, ...]
    flaky_by_priority: dict[str, int] = field(default_factory=dict)


def _trend(runs: Sequence[RunResult]) -> tuple[TrendPoint, ...]:
    return tuple(
        TrendPoint(
            run_key=r.key,
            started_at=r.run.started_at,
            commit_sha=r.run.commit_sha,
            run_url=r.run.run_url,
            executed=r.summary.executed,
            passed=r.summary.passed,
            flaky=r.summary.flaky,
            failed=r.summary.failed,
            blocked=r.summary.blocked,
            skipped=r.summary.skipped,
            not_run=r.summary.not_run,
            retries=r.summary.retries,
            gate=r.gate.decision.value if r.gate else "n/a",
        )
        for r in runs
    )


def _case_history(runs: Sequence[RunResult]) -> dict[str, tuple[CaseRunView, ...]]:
    history: dict[str, list[CaseRunView]] = {}
    for run in runs:
        for case in run.cases:
            attempts = [a for e in case.executions for a in e.attempts]
            history.setdefault(case.case_id, []).append(
                CaseRunView(
                    run_key=run.key,
                    started_at=run.run.started_at,
                    commit_sha=run.run.commit_sha,
                    run_url=run.run.run_url,
                    status=case.final_status,
                    attempts=len(attempts),
                    messages=tuple(a.message for a in attempts if a.message),
                    evidence=tuple(ev for a in attempts for ev in a.evidence),
                )
            )
    return {cid: tuple(reversed(views)) for cid, views in history.items()}


def _environment_label(run: RunResult) -> str:
    browser = run.environment.browser
    b = f" · {browser.name} {browser.version or ''}".rstrip() if browser else ""
    return f"{run.environment.kind} / {run.environment.os}{b}"


def _performance(runs: Sequence[RunResult]) -> tuple[PerfSeriesView, ...]:
    series: dict[tuple[str, str], list[tuple[RunResult, list[float]]]] = {}
    for run in runs:
        for s in run.performance:
            if s.samples:
                series.setdefault((s.case_id, s.series), []).append((run, list(s.samples)))
    views = []
    for (case_id, name), points in sorted(series.items()):
        latest_run, latest_samples = points[-1]
        env = _environment_label(latest_run)
        comparable = [(r, smp) for r, smp in points if _environment_label(r) == env]
        medians = [describe(smp).median or 0.0 for _, smp in comparable]
        latest_stats = describe(latest_samples)
        baseline = compute_baseline(medians[:-1]) if len(medians) > 1 else None
        views.append(
            PerfSeriesView(
                case_id=case_id,
                series=name,
                latest=latest_stats,
                latest_run_key=latest_run.key,
                environment=env,
                comparison=compare(latest_stats.median, baseline),
                history=tuple((r.run.started_at, m) for (r, _), m in zip(comparable, medians, strict=True)),
            )
        )
    return tuple(views)


def build_dashboard(runs: Sequence[RunResult], generated_at: datetime) -> DashboardModel:
    functional = sorted((r for r in runs if r.run.scope == "functional"), key=lambda r: r.run.started_at)
    performance = sorted((r for r in runs if r.run.scope == "performance"), key=lambda r: r.run.started_at)
    stability = analyze_stability(functional)
    flaky_by_priority: dict[str, int] = {}
    if functional:
        for case in functional[-1].cases:
            if case.final_status is FinalStatus.FLAKY:
                flaky_by_priority[case.priority] = flaky_by_priority.get(case.priority, 0) + 1
    return DashboardModel(
        generated_at=generated_at,
        has_functional_data=bool(functional),
        has_performance_data=bool(performance),
        latest_functional=functional[-1] if functional else None,
        latest_performance=performance[-1] if performance else None,
        trend=_trend(functional),
        stability=stability,
        top_unstable=tuple(top_unstable(stability.values())),
        case_history=_case_history(functional + performance),
        performance=_performance(performance),
        flaky_by_priority=flaky_by_priority,
    )
