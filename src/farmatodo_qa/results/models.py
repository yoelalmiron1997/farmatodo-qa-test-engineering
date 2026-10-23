"""Esquema ``run-result`` v1 (SDD Anexo E.2).

Se define una sola vez con Pydantic; el JSON Schema publicado se exporta desde aquí
(``qa results schema``), así el contrato no se duplica.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = 1


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class AttemptOutcome(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class FinalStatus(StrEnum):
    PASS = "PASS"
    FLAKY = "FLAKY"
    FAIL = "FAIL"
    SKIPPED = "SKIPPED"
    BLOCKED = "BLOCKED"
    NOT_RUN = "NOT_RUN"


EXECUTED_STATUSES = frozenset({FinalStatus.PASS, FinalStatus.FLAKY, FinalStatus.FAIL})


class FailureCategory(StrEnum):
    ASSERTION = "assertion"
    TIMEOUT = "timeout"
    ELEMENT_NOT_FOUND = "element_not_found"
    STALE_ELEMENT = "stale_element"
    BROWSER_DRIVER = "browser_driver"
    NETWORK = "network"
    EXTERNAL_DEPENDENCY = "external_dependency"
    UNKNOWN = "unknown"


class Attempt(_Model):
    n: int = Field(ge=1)
    outcome: AttemptOutcome
    duration_s: float = Field(ge=0)
    started_at: datetime | None = None
    phase: Literal["setup", "call", "teardown"] = "call"
    exception_type: str | None = None
    message: str | None = Field(default=None, max_length=4000)
    category: FailureCategory | None = None
    evidence: list[str] = Field(default_factory=list)


class TestExecution(_Model):
    """Una función de test concreta (un parámetro) con todos sus intentos."""

    nodeid: str
    param_id: str | None = None
    final_status: FinalStatus
    attempts: list[Attempt] = Field(default_factory=list)
    blocked_reason: str | None = None


class CaseResult(_Model):
    case_id: str = Field(pattern=r"^TC-[A-Z]+-\d{3}$")
    title: str
    priority: Literal["P0", "P1", "P2"]
    level: str
    spec_hash: str
    known_defect: str | None = None
    final_status: FinalStatus
    executions: list[TestExecution] = Field(default_factory=list)


class PerformanceSeries(_Model):
    case_id: str
    series: Literal[
        "navigation_load", "navigation_ttfb", "navigation_dcl", "editor_ready", "end_to_end", "in_browser"
    ]
    unit: Literal["ms"] = "ms"
    samples: list[float] = Field(default_factory=list)
    invalid_samples: int = 0
    warmup_discarded: int = 0
    poll_resolution_ms: float | None = None


class RunInfo(_Model):
    run_id: str
    run_attempt: int = Field(default=1, ge=1)
    workflow: str
    scope: Literal["functional", "performance"]
    trigger: str
    commit_sha: str
    ref: str | None = None
    repository: str | None = None
    run_url: str | None = None
    started_at: datetime
    finished_at: datetime
    random_seed: int | None = None
    reruns_configured: int = 0


class BrowserInfo(_Model):
    name: str
    version: str | None = None
    driver_version: str | None = None
    headless: bool = True
    viewport: str | None = None


class Environment(_Model):
    kind: str
    os: str
    python: str
    pytest: str | None = None
    selenium: str | None = None
    browser: BrowserInfo | None = None
    target_urls: list[str] = Field(default_factory=list)


class Summary(_Model):
    specified: int
    executed: int
    passed: int
    flaky: int
    failed: int
    skipped: int
    blocked: int
    not_run: int
    attempts: int
    retries: int
    cases_with_retries: int
    flaky_rate: float | None
    first_attempt_pass_rate: float | None
    final_pass_rate: float | None
    duration_s: float
    mean_case_duration_s: float | None
    failures_by_category: dict[str, int] = Field(default_factory=dict)


class GateDecision(StrEnum):
    PASS = "pass"
    WARN = "warn"
    INCONCLUSIVE = "inconclusive"
    BLOCK = "block"


class GateResult(_Model):
    decision: GateDecision
    reasons: list[str] = Field(default_factory=list)


class RunResult(_Model):
    schema_version: Literal[1] = 1  # == SCHEMA_VERSION
    run: RunInfo
    environment: Environment
    cases: list[CaseResult]
    performance: list[PerformanceSeries] = Field(default_factory=list)
    summary: Summary
    gate: GateResult | None = None

    @property
    def key(self) -> str:
        return f"{self.run.run_id}-{self.run.run_attempt}"
