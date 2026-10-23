"""Modelo normalizado de resultados (esquema versionado) y su construcción."""

from farmatodo_qa.results.models import (
    SCHEMA_VERSION,
    Attempt,
    AttemptOutcome,
    CaseResult,
    Environment,
    FinalStatus,
    GateDecision,
    GateResult,
    PerformanceSeries,
    RunInfo,
    RunResult,
    Summary,
    TestExecution,
)

__all__ = [
    "SCHEMA_VERSION",
    "Attempt",
    "AttemptOutcome",
    "CaseResult",
    "Environment",
    "FinalStatus",
    "GateDecision",
    "GateResult",
    "PerformanceSeries",
    "RunInfo",
    "RunResult",
    "Summary",
    "TestExecution",
]
