"""Clasificación del estado final a partir de los intentos (SDD Anexo C.2).

Reglas:
* sin intentos → NOT_RUN
* último intento BLOCKED → BLOCKED; último SKIPPED → SKIPPED
* último PASSED → FLAKY si hubo algún fallo previo en la misma corrida; si no, PASS
* último FAILED → FAIL (un timeout que termina fallando es FAIL, nunca FLAKY)
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from farmatodo_qa.results.models import AttemptOutcome, FinalStatus

# Severidad para agregar varias ejecuciones (parámetros) de un mismo caso.
_SEVERITY: dict[FinalStatus, int] = {
    FinalStatus.FAIL: 5,
    FinalStatus.FLAKY: 4,
    FinalStatus.BLOCKED: 3,
    FinalStatus.NOT_RUN: 2,
    FinalStatus.PASS: 1,
    FinalStatus.SKIPPED: 0,
}


def classify_attempts(outcomes: Sequence[AttemptOutcome]) -> FinalStatus:
    if not outcomes:
        return FinalStatus.NOT_RUN
    last = outcomes[-1]
    if last is AttemptOutcome.BLOCKED:
        return FinalStatus.BLOCKED
    if last is AttemptOutcome.SKIPPED:
        return FinalStatus.SKIPPED
    if last is AttemptOutcome.PASSED:
        failed_before = any(outcome is AttemptOutcome.FAILED for outcome in outcomes[:-1])
        return FinalStatus.FLAKY if failed_before else FinalStatus.PASS
    return FinalStatus.FAIL


def aggregate_statuses(statuses: Iterable[FinalStatus]) -> FinalStatus:
    """El estado de un caso es el más severo de sus ejecuciones."""
    collected = list(statuses)
    if not collected:
        return FinalStatus.NOT_RUN
    return max(collected, key=lambda status: _SEVERITY[status])
