"""Constructores de datos sintéticos para probar el framework sin navegador."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from farmatodo_qa.metrics.flaky.classifier import aggregate_statuses, classify_attempts
from farmatodo_qa.metrics.summary import compute_summary
from farmatodo_qa.results.models import (
    Attempt,
    AttemptOutcome,
    BrowserInfo,
    CaseResult,
    Environment,
    FailureCategory,
    FinalStatus,
    PerformanceSeries,
    RunInfo,
    RunResult,
    TestExecution,
)

T0 = datetime(2026, 10, 23, 12, 0, tzinfo=UTC)
O = AttemptOutcome


def attempts(*outcomes: AttemptOutcome, message: str = "esperado 9, actual 8") -> list[Attempt]:
    out = []
    for n, outcome in enumerate(outcomes, start=1):
        failed = outcome is O.FAILED
        out.append(
            Attempt(
                n=n,
                outcome=outcome,
                duration_s=1.0,
                exception_type="AssertionError" if failed else None,
                message=message if failed else None,
                category=FailureCategory.ASSERTION if failed else None,
                evidence=[f"evidence/a{n}.png"] if failed else [],
            )
        )
    return out


def case(
    case_id: str,
    *outcome_lists: tuple[AttemptOutcome, ...],
    priority: str = "P0",
    known_defect: str | None = None,
    spec_hash: str = "sha256:abc",
    title: str | None = None,
) -> CaseResult:
    executions = []
    for index, outcomes in enumerate(outcome_lists):
        atts = attempts(*outcomes)
        executions.append(
            TestExecution(
                nodeid=f"tests/e2e/test_x.py::test_{case_id}[p{index}]",
                param_id=f"p{index}",
                final_status=classify_attempts([a.outcome for a in atts]),
                attempts=atts,
                blocked_reason="sitio inaccesible" if outcomes and outcomes[-1] is O.BLOCKED else None,
            )
        )
    return CaseResult(
        case_id=case_id,
        title=title or f"Caso {case_id}",
        priority=priority,  # type: ignore[arg-type]
        level="e2e",
        spec_hash=spec_hash,
        known_defect=known_defect,
        final_status=aggregate_statuses(e.final_status for e in executions)
        if executions
        else FinalStatus.NOT_RUN,
        executions=executions,
    )


def run(
    cases: list[CaseResult],
    *,
    run_id: str = "100",
    started: datetime = T0,
    scope: str = "functional",
    performance: list[PerformanceSeries] | None = None,
    browser_version: str = "152.0.1",
) -> RunResult:
    finished = started + timedelta(minutes=5)
    return RunResult(
        run=RunInfo(
            run_id=run_id,
            run_attempt=1,
            workflow="functional-tests" if scope == "functional" else "performance",
            scope=scope,  # type: ignore[arg-type]
            trigger="push",
            commit_sha="0123456789abcdef",
            run_url=f"https://github.com/o/r/actions/runs/{run_id}",
            started_at=started,
            finished_at=finished,
        ),
        environment=Environment(
            kind="github-actions",
            os="ubuntu24",
            python="3.12.13",
            browser=BrowserInfo(name="chrome", version=browser_version),
        ),
        cases=cases,
        performance=performance or [],
        summary=compute_summary(cases, started, finished),
    )
