"""Modelos de especificación (schema v1, SDD §9.1)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Priority = Literal["P0", "P1", "P2"]
PRIORITIES: tuple[str, ...] = ("P0", "P1", "P2")
REQUIRED_SECTIONS: tuple[str, ...] = (
    "## Objetivo",
    "## Justificación de la prioridad",
    "## Precondiciones",
    "## Datos de entrada",
    "## Pasos",
    "## Resultado esperado",
    "## Criterio de aceptación",
    "## Evidencias esperadas",
)
AUTOMATED = frozenset({"planned", "implemented"})


def rule_priority(score: int) -> str:
    """Regla reproducible del SDD §7.1: P0 >= 15, P1 8–14, P2 <= 7."""
    if score >= 15:
        return "P0"
    if score >= 8:
        return "P1"
    return "P2"


def risk_level(score: int) -> str:
    if score >= 15:
        return "high"
    if score >= 8:
        return "medium"
    return "low"


class _Spec(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Requirement(_Spec):
    id: str = Field(pattern=r"^REQ-[A-Z]+-\d{3}$")
    source: str
    exercise: str
    verification: Literal["test", "inspection", "analysis", "demonstration"]
    statement: str
    acceptance_criteria: list[str] = Field(min_length=1)


class RiskAssessment(_Spec):
    impact: int = Field(ge=1, le=5)
    likelihood: int = Field(ge=1, le=5)
    score: int = Field(ge=1, le=25)
    computed_priority: Priority


class CaseFrontMatter(_Spec):
    id: str = Field(pattern=r"^TC-[A-Z]+-\d{3}$")
    title: str = Field(min_length=3)
    requirement_ids: list[str] = Field(min_length=1)
    priority: Priority
    test_type: Literal["functional", "non-functional", "performance", "exploratory"]
    level: Literal["unit", "integration", "e2e", "manual"]
    automation: Literal["planned", "implemented", "manual", "not-automatable"]
    risk: Literal["high", "medium", "low"]
    risk_assessment: RiskAssessment
    priority_override_reason: str | None = None
    techniques: list[str] = Field(min_length=1)
    mandatory_deliverable: bool = False
    known_defect: str | None = Field(default=None, pattern=r"^BUG-[A-Z]+-\d{3}$")
    external_dependencies: list[str] = Field(default_factory=list)
    hypotheses: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    status: Literal["draft", "approved", "deprecated"]
    spec_version: int = Field(ge=1)


class CaseSpec(_Spec):
    meta: CaseFrontMatter
    body: str
    path: str
    spec_hash: str

    @property
    def id(self) -> str:
        return self.meta.id

    @property
    def is_automated(self) -> bool:
        return self.meta.automation in AUTOMATED


class BugReport(_Spec):
    id: str = Field(pattern=r"^(BUG|OBS)-[A-Z]+-\d{3}$")
    title: str
    type: Literal["defect", "improvement"]
    severity: Literal["critical", "major", "minor", "trivial"] | None = None
    priority: Literal["high", "medium", "low"]
    status: Literal["confirmed", "open", "closed"]
    related_cases: list[str] = Field(default_factory=list)
    environment: dict[str, str] = Field(default_factory=dict)
    path: str = ""


class ImplementationRef(_Spec):
    case_id: str
    path: str
    line: int
    test_name: str
