"""Indicadores de una corrida con fórmulas y denominadores explícitos (SDD Anexo A.6).

Unidades: los conteos de estado son **casos**; ``attempts`` y ``retries`` son **intentos**
de cada ejecución de test (un caso parametrizado tiene varias ejecuciones).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from datetime import datetime

from farmatodo_qa.results.models import (
    EXECUTED_STATUSES,
    AttemptOutcome,
    CaseResult,
    FinalStatus,
    Summary,
)


def _ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def compute_summary(cases: Sequence[CaseResult], started_at: datetime, finished_at: datetime) -> Summary:
    status_counts = Counter(case.final_status for case in cases)
    executed_cases = [case for case in cases if case.final_status in EXECUTED_STATUSES]
    executed = len(executed_cases)

    attempts = retries = 0
    cases_with_retries = 0
    total_duration = 0.0
    categories: Counter[str] = Counter()
    for case in executed_cases:
        retried = False
        for execution in case.executions:
            attempts += len(execution.attempts)
            extra = max(0, len(execution.attempts) - 1)
            retries += extra
            retried = retried or extra > 0
            for attempt in execution.attempts:
                total_duration += attempt.duration_s
                if attempt.outcome is AttemptOutcome.FAILED:
                    categories[(attempt.category or "unknown").__str__()] += 1
        cases_with_retries += int(retried)

    passed = status_counts[FinalStatus.PASS]
    flaky = status_counts[FinalStatus.FLAKY]
    return Summary(
        specified=len(cases),
        executed=executed,
        passed=passed,
        flaky=flaky,
        failed=status_counts[FinalStatus.FAIL],
        skipped=status_counts[FinalStatus.SKIPPED],
        blocked=status_counts[FinalStatus.BLOCKED],
        not_run=status_counts[FinalStatus.NOT_RUN],
        attempts=attempts,
        retries=retries,
        cases_with_retries=cases_with_retries,
        flaky_rate=_ratio(flaky, executed),
        first_attempt_pass_rate=_ratio(passed, executed),
        final_pass_rate=_ratio(passed + flaky, executed),
        duration_s=max(0.0, (finished_at - started_at).total_seconds()),
        mean_case_duration_s=total_duration / executed if executed else None,
        failures_by_category=dict(sorted(categories.items())),
    )
