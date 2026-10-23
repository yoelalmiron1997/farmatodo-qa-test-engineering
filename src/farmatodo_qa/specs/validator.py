"""Reglas de consistencia de especificaciones y trazabilidad (SDD §10.3).

Función pura: recibe las especificaciones ya cargadas y devuelve una lista de problemas.
Cada grupo de reglas es una función independiente.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import PurePosixPath

from farmatodo_qa.specs.models import (
    REQUIRED_SECTIONS,
    BugReport,
    CaseSpec,
    ImplementationRef,
    Requirement,
    rule_priority,
)


@dataclass(frozen=True, slots=True)
class Issue:
    code: str
    message: str
    location: str = ""

    def __str__(self) -> str:
        where = f" [{self.location}]" if self.location else ""
        return f"{self.code}{where}: {self.message}"


def _duplicates(ids: Iterable[str], kind: str) -> list[Issue]:
    return [
        Issue("SPEC003", f"ID de {kind} duplicado ({n} veces)", dup)
        for dup, n in Counter(ids).items()
        if n > 1
    ]


def _check_case(case: CaseSpec, req_ids: set[str]) -> list[Issue]:
    meta = case.meta
    issues: list[Issue] = []
    if PurePosixPath(case.path).stem != meta.id:
        issues.append(Issue("SPEC002", f"el archivo debe llamarse {meta.id}.md", case.path))
    issues += [
        Issue("SPEC001", f"falta la sección '{section}'", meta.id)
        for section in REQUIRED_SECTIONS
        if section not in case.body
    ]
    issues += [
        Issue("TRC001", f"requisito inexistente {rid}", meta.id)
        for rid in meta.requirement_ids
        if rid not in req_ids
    ]
    ra = meta.risk_assessment
    computed = rule_priority(ra.impact * ra.likelihood)
    if ra.score != ra.impact * ra.likelihood:
        issues.append(Issue("PRI003", "score != impact × likelihood", meta.id))
    if ra.computed_priority != computed:
        issues.append(Issue("PRI003", f"computed_priority debería ser {computed}", meta.id))
    if meta.priority != computed and not meta.priority_override_reason:
        issues.append(
            Issue(
                "PRI002",
                f"prioridad {meta.priority} ≠ regla {computed} sin priority_override_reason",
                meta.id,
            )
        )
    return issues


def _check_requirements(requirements: Sequence[Requirement], cases: Sequence[CaseSpec]) -> list[Issue]:
    covered = {rid for case in cases for rid in case.meta.requirement_ids}
    return [
        Issue("TRC002", "requisito verificable por test sin casos", req.id)
        for req in requirements
        if req.verification == "test" and req.id not in covered
    ]


def _check_implementations(
    cases: Sequence[CaseSpec],
    implementations: Sequence[ImplementationRef],
    unmarked_tests: Sequence[str],
    existing_paths: frozenset[str] | None,
) -> list[Issue]:
    implemented = {ref.case_id for ref in implementations}
    known = {case.id for case in cases}
    issues: list[Issue] = []
    for case in cases:
        if case.meta.level != "manual" and case.is_automated and case.id not in implemented:
            issues.append(Issue("IMP001", "caso automatizable sin test con su marker", case.id))
        if case.meta.automation == "manual" and case.id in implemented:
            issues.append(Issue("IMP004", "caso manual con implementación automatizada", case.id))
    for ref in implementations:
        if ref.case_id not in known:
            issues.append(
                Issue("IMP002", f"marker con caso inexistente {ref.case_id}", f"{ref.path}:{ref.line}")
            )
        if existing_paths is not None and ref.path not in existing_paths:
            issues.append(Issue("IMP003", "enlace de implementación inválido", ref.path))
    issues += [Issue("IMP002", "test sin marker case", test) for test in unmarked_tests]
    return issues


def _check_bugs(cases: Sequence[CaseSpec], bugs: Sequence[BugReport]) -> list[Issue]:
    known = {case.id for case in cases}
    bug_ids = {bug.id for bug in bugs}
    issues = [
        Issue("TRC004", f"defecto vinculado a caso inexistente {cid}", bug.id)
        for bug in bugs
        for cid in bug.related_cases
        if cid not in known
    ]
    if bugs:
        issues += [
            Issue("TRC004", f"known_defect {case.meta.known_defect} sin reporte", case.id)
            for case in cases
            if case.meta.known_defect and case.meta.known_defect not in bug_ids
        ]
    return issues


def validate(
    requirements: Sequence[Requirement],
    cases: Sequence[CaseSpec],
    implementations: Sequence[ImplementationRef],
    unmarked_tests: Sequence[str],
    *,
    bugs: Sequence[BugReport] = (),
    existing_paths: frozenset[str] | None = None,
) -> list[Issue]:
    req_ids = {r.id for r in requirements}
    issues = _duplicates((c.id for c in cases), "caso") + _duplicates(
        (r.id for r in requirements), "requisito"
    )
    for case in cases:
        issues += _check_case(case, req_ids)
    issues += _check_requirements(requirements, cases)
    issues += _check_implementations(cases, implementations, unmarked_tests, existing_paths)
    issues += _check_bugs(cases, bugs)
    return issues
