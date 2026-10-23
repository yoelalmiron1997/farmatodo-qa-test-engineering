"""Registros crudos por intento (JSONL del plugin) → :class:`RunResult` validado."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from farmatodo_qa.metrics.flaky.classifier import aggregate_statuses, classify_attempts
from farmatodo_qa.metrics.flaky.failure_categories import categorize
from farmatodo_qa.metrics.summary import compute_summary
from farmatodo_qa.results.models import (
    Attempt,
    AttemptOutcome,
    CaseResult,
    Environment,
    FinalStatus,
    PerformanceSeries,
    RunInfo,
    RunResult,
    TestExecution,
)

Scope = Literal["functional", "performance"]


@dataclass(frozen=True, slots=True)
class CatalogEntry:
    """Lo mínimo del catálogo que necesita la normalización (desacoplado de ``specs``)."""

    case_id: str
    title: str
    priority: Literal["P0", "P1", "P2"]
    level: str
    test_type: str
    automated: bool
    spec_hash: str
    known_defect: str | None = None

    def in_scope(self, scope: Scope, levels: frozenset[str] | None = None) -> bool:
        if not self.automated or self.level == "manual":
            return False
        if levels is not None and self.level not in levels:
            return False
        is_perf = self.test_type == "performance"
        return is_perf if scope == "performance" else not is_perf


@dataclass(frozen=True, slots=True)
class NormalizationIssue:
    code: str
    message: str


def _to_attempt(record: Mapping[str, Any]) -> Attempt:
    outcome = AttemptOutcome(record["outcome"])
    category = None
    if outcome is AttemptOutcome.FAILED:
        category = categorize(record.get("exception_type"), record.get("message"))
    elif outcome is AttemptOutcome.BLOCKED:
        category = categorize("BlockedPrecondition", None)
    return Attempt(
        n=int(record["attempt"]),
        outcome=outcome,
        duration_s=float(record.get("duration_s") or 0.0),
        started_at=record.get("started_at"),
        phase=record.get("phase", "call"),
        exception_type=record.get("exception_type"),
        message=(record.get("message") or None) and str(record["message"])[:4000],
        category=category,
        evidence=list(record.get("evidence") or []),
    )


def build_run_result(
    records: Iterable[Mapping[str, Any]],
    catalog: Mapping[str, CatalogEntry],
    run: RunInfo,
    environment: Environment,
    *,
    performance: Sequence[PerformanceSeries] = (),
    levels: frozenset[str] | None = None,
) -> tuple[RunResult, list[NormalizationIssue]]:
    """``levels`` limita qué casos sin registros cuentan como NOT_RUN (p. ej. una corrida solo E2E)."""
    issues: list[NormalizationIssue] = []
    by_node: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    node_case: dict[str, str] = {}
    for record in records:
        case_id = record.get("case_id")
        if not case_id:
            issues.append(NormalizationIssue("RES001", f"resultado sin case_id: {record.get('nodeid')}"))
            continue
        if case_id not in catalog:
            issues.append(
                NormalizationIssue("RES002", f"case_id desconocido {case_id}: {record.get('nodeid')}")
            )
            continue
        by_node[record["nodeid"]].append(record)
        node_case[record["nodeid"]] = case_id

    executions: dict[str, list[TestExecution]] = defaultdict(list)
    for nodeid, node_records in by_node.items():
        attempts = [_to_attempt(r) for r in sorted(node_records, key=lambda r: int(r["attempt"]))]
        blocked = next((r.get("blocked_reason") for r in node_records if r.get("blocked_reason")), None)
        executions[node_case[nodeid]].append(
            TestExecution(
                nodeid=nodeid,
                param_id=node_records[0].get("param_id"),
                final_status=classify_attempts([a.outcome for a in attempts]),
                attempts=attempts,
                blocked_reason=blocked,
            )
        )

    cases: list[CaseResult] = []
    for entry in sorted(catalog.values(), key=lambda e: e.case_id):
        case_execs = sorted(executions.get(entry.case_id, []), key=lambda e: e.nodeid)
        if not case_execs and not entry.in_scope(run.scope, levels):
            continue
        cases.append(
            CaseResult(
                case_id=entry.case_id,
                title=entry.title,
                priority=entry.priority,
                level=entry.level,
                spec_hash=entry.spec_hash,
                known_defect=entry.known_defect,
                final_status=aggregate_statuses(e.final_status for e in case_execs)
                if case_execs
                else FinalStatus.NOT_RUN,
                executions=case_execs,
            )
        )

    summary = compute_summary(cases, run.started_at, run.finished_at)
    result = RunResult(
        run=run, environment=environment, cases=cases, performance=list(performance), summary=summary
    )
    return result, issues
