"""Vistas generadas a partir de las especificaciones (catálogo, matriz, cobertura).

Fuente única: ``specs/cases/*.md`` y ``requirements.yaml``. Los bloques del SDD se regeneran
con esto y el CI falla si el contenido versionado difiere (GEN001).
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from farmatodo_qa.specs.models import CaseSpec, ImplementationRef, Requirement

_PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2}
_BLOCK_RE = r"(<!-- BEGIN GENERATED: {name}[^\n]*-->\n)(.*?)(\n<!-- END GENERATED: {name} -->)"


def _first_sentence(text: str) -> str:
    sentence = re.split(r"(?<=\.)\s", text.strip(), maxsplit=1)[0]
    return sentence if sentence.endswith(".") else sentence + "."


def _justification(case: CaseSpec) -> str:
    if case.meta.priority_override_reason:
        return case.meta.priority_override_reason
    match = re.search(r"## Justificación de la prioridad\n.*?\n\n(.*?)\n\n## ", case.body, re.S)
    return _first_sentence(match.group(1)) if match else "—"


def automation_label(case: CaseSpec, implemented: set[str]) -> str:
    if case.meta.automation == "manual":
        return "No — manual"
    state = "implementado" if case.id in implemented else "planificado"
    return f"Sí ({case.meta.level}, {state})"


def render_inventory(cases: Sequence[CaseSpec], implemented: set[str], link_prefix: str = "cases/") -> str:
    rows = [
        "| ID | Requisito(s) | Escenario | Riesgo (I×P) | Prioridad | Técnica | Automatizable | Justificación |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for case in cases:
        meta = case.meta
        ra = meta.risk_assessment
        star = "*" if meta.priority_override_reason else ""
        rows.append(
            f"| [{meta.id}]({link_prefix}{meta.id}.md) | {', '.join(meta.requirement_ids)} | {meta.title} | "
            f"{meta.risk} ({ra.impact}×{ra.likelihood}={ra.score}) | **{meta.priority}**{star} | "
            f"{', '.join(meta.techniques)} | {automation_label(case, implemented)} | {_justification(case)} |"
        )
    return "\n".join(rows)


def cases_for(requirement_id: str, cases: Sequence[CaseSpec]) -> list[CaseSpec]:
    return [c for c in cases if requirement_id in c.meta.requirement_ids]


def render_traceability(
    requirements: Sequence[Requirement],
    cases: Sequence[CaseSpec],
    statuses: Mapping[str, str] | None = None,
    link_prefix: str = "cases/",
) -> str:
    statuses = statuses or {}
    rows = [
        "| Requisito | Fuente | Verificación | Casos | Prioridad máx. | Estado |",
        "|---|---|---|---|---|---|",
    ]
    for req in requirements:
        related = cases_for(req.id, cases)
        links = ", ".join(f"[{c.id}]({link_prefix}{c.id}.md)" for c in related)
        top = min((c.meta.priority for c in related), key=_PRIORITY_ORDER.__getitem__, default="—")
        if related:
            state = ", ".join(sorted({statuses.get(c.id, "No ejecutado") for c in related}))
        else:
            state = f"Verificación por {req.verification}"
        rows.append(f"| {req.id} | {req.source} | {req.verification} | {links or '—'} | {top} | {state} |")
    return "\n".join(rows)


def catalog_summary(cases: Sequence[CaseSpec], requirements: Sequence[Requirement]) -> str:
    by_priority = {p: sum(1 for c in cases if c.meta.priority == p) for p in _PRIORITY_ORDER}
    by_level: dict[str, int] = {}
    for c in cases:
        by_level[c.meta.level] = by_level.get(c.meta.level, 0) + 1
    levels = " · ".join(f"{k}: {v}" for k, v in sorted(by_level.items()))
    return (
        f"**{len(cases)} casos** · P0: {by_priority['P0']} · P1: {by_priority['P1']} · "
        f"P2: {by_priority['P2']} · {levels} · requisitos: {len(requirements)}"
    )


def replace_generated_block(document: str, name: str, content: str) -> str:
    pattern = re.compile(_BLOCK_RE.format(name=re.escape(name)), re.S)
    if not pattern.search(document):
        raise KeyError(f"bloque generado '{name}' no encontrado")
    return pattern.sub(lambda m: m.group(1) + content + m.group(3), document, count=1)


def implemented_ids(refs: Sequence[ImplementationRef]) -> set[str]:
    return {r.case_id for r in refs}


@dataclass(frozen=True, slots=True)
class Coverage:
    label: str
    numerator: int
    denominator: int

    @property
    def ratio(self) -> float | None:
        return self.numerator / self.denominator if self.denominator else None


def specification_coverage(requirements: Sequence[Requirement], cases: Sequence[CaseSpec]) -> list[Coverage]:
    """Requisitos con ≥ 1 caso o verificación no-test declarada, separados por origen."""
    out = []
    for label, pick in (
        ("PDF", lambda r: not r.id.startswith("REQ-QA")),
        ("Derivados", lambda r: r.id.startswith("REQ-QA")),
    ):
        group = [r for r in requirements if pick(r)]
        ok = [r for r in group if r.verification != "test" or cases_for(r.id, cases)]
        out.append(Coverage(f"Requisitos {label} especificados", len(ok), len(group)))
    return out


def automation_coverage(cases: Sequence[CaseSpec], implemented: set[str]) -> list[Coverage]:
    out = []
    for priority in _PRIORITY_ORDER:
        automatable = [
            c for c in cases if c.meta.priority == priority and c.is_automated and c.meta.level != "manual"
        ]
        done = [c for c in automatable if c.id in implemented]
        out.append(Coverage(f"Automatización {priority}", len(done), len(automatable)))
    return out
