"""Validador de especificaciones y trazabilidad (TC-FW-004)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from farmatodo_qa.specs.loader import SpecError, split_front_matter
from farmatodo_qa.specs.models import (
    REQUIRED_SECTIONS,
    CaseFrontMatter,
    CaseSpec,
    ImplementationRef,
    Requirement,
)
from farmatodo_qa.specs.validator import validate
from farmatodo_qa.traceability.catalog import replace_generated_block
from farmatodo_qa.traceability.implementation_scan import scan_source

BODY = "\n\n".join(f"{s}\nx" for s in REQUIRED_SECTIONS)
REQ = Requirement(
    id="REQ-WC-001",
    source="PDF",
    exercise="E1",
    verification="test",
    statement="s",
    acceptance_criteria=["a"],
)


def make_case(
    case_id: str = "TC-WC-001", path: str | None = None, body: str = BODY, **overrides: Any
) -> CaseSpec:
    meta: dict[str, Any] = {
        "id": case_id,
        "title": "Caso de prueba",
        "requirement_ids": ["REQ-WC-001"],
        "priority": "P0",
        "test_type": "functional",
        "level": "e2e",
        "automation": "planned",
        "risk": "high",
        "risk_assessment": {"impact": 5, "likelihood": 3, "score": 15, "computed_priority": "P0"},
        "techniques": ["Partición de equivalencia"],
        "status": "draft",
        "spec_version": 1,
    }
    meta.update(overrides)
    return CaseSpec(
        meta=CaseFrontMatter.model_validate(meta),
        body=body,
        path=path or f"specs/cases/{case_id}.md",
        spec_hash="h",
    )


def ref(case_id: str = "TC-WC-001") -> ImplementationRef:
    return ImplementationRef(case_id=case_id, path="tests/e2e/test_x.py", line=1, test_name="test_x")


def codes(**kwargs: Any) -> list[str]:
    params: dict[str, Any] = {
        "requirements": [REQ],
        "cases": [make_case()],
        "implementations": [ref()],
        "unmarked_tests": [],
    }
    params.update(kwargs)
    return sorted(issue.code for issue in validate(**params))


@pytest.mark.case("TC-FW-004")
def test_valid_specs_have_no_issues() -> None:
    assert codes() == []


@pytest.mark.case("TC-FW-004")
@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        ({"cases": [make_case(), make_case()], "implementations": [ref()]}, ["SPEC003"]),
        ({"cases": [make_case(path="specs/cases/otro.md")]}, ["SPEC002"]),
        ({"cases": [make_case(body="## Objetivo\nx")]}, ["SPEC001"] * (len(REQUIRED_SECTIONS) - 1)),
        ({"cases": [make_case(requirement_ids=["REQ-WC-999"])]}, ["TRC001", "TRC002"]),
        ({"cases": [make_case(priority="P1")]}, ["PRI002"]),
        ({"cases": [make_case(priority="P1", priority_override_reason="obligatorio")]}, []),
        ({"implementations": []}, ["IMP001"]),
        ({"implementations": [ref(), ref("TC-WC-404")]}, ["IMP002"]),
        ({"unmarked_tests": ["tests/e2e/test_x.py::test_sin_marker"]}, ["IMP002"]),
        ({"existing_paths": frozenset()}, ["IMP003"]),
    ],
    ids=[
        "id-duplicado",
        "nombre-archivo",
        "secciones",
        "requisito-inexistente",
        "prioridad-sin-override",
        "override-justificado",
        "automatizado-sin-test",
        "marker-huerfano",
        "test-sin-marker",
        "enlace-invalido",
    ],
)
def test_each_inconsistency_is_detected(kwargs: dict[str, Any], expected: list[str]) -> None:
    assert codes(**kwargs) == sorted(expected)


@pytest.mark.case("TC-FW-004")
def test_unknown_priority_is_rejected_by_schema() -> None:
    with pytest.raises(ValueError, match="priority"):
        make_case(priority="P9")


@pytest.mark.case("TC-FW-004")
def test_missing_required_field_is_rejected() -> None:
    with pytest.raises(ValueError, match="title"):
        CaseFrontMatter.model_validate({"id": "TC-WC-001"})


@pytest.mark.case("TC-FW-004")
def test_front_matter_must_exist() -> None:
    with pytest.raises(SpecError):
        split_front_matter("# sin front matter", "x.md")


@pytest.mark.case("TC-FW-004")
def test_marker_scanner_finds_decorators_params_and_unmarked_tests() -> None:
    source = """
import pytest
pytestmark = [pytest.mark.e2e]

@pytest.mark.case("TC-WC-001")
@pytest.mark.parametrize("x", [1])
def test_a(x): ...

def test_b(): ...

class TestGroup:
    @pytest.mark.case("TC-WC-002")
    def test_c(self): ...
"""
    refs, unmarked = scan_source("tests/e2e/test_s.py", source)
    assert [(r.case_id, r.test_name) for r in refs] == [("TC-WC-001", "test_a"), ("TC-WC-002", "test_c")]
    assert unmarked == ["tests/e2e/test_s.py::test_b"]


@pytest.mark.case("TC-FW-004")
def test_generated_block_replacement_is_idempotent() -> None:
    doc = "a\n<!-- BEGIN GENERATED: inventory — no editar -->\nviejo\n<!-- END GENERATED: inventory -->\nb"
    once = replace_generated_block(doc, "inventory", "nuevo")
    assert "nuevo" in once
    assert "viejo" not in once
    assert replace_generated_block(once, "inventory", "nuevo") == once


@pytest.mark.case("TC-FW-004")
def test_real_repository_specs_are_consistent() -> None:
    """Las especificaciones versionadas del propio repositorio pasan la validación."""
    from farmatodo_qa.cli import main

    root = Path(__file__).resolve().parents[3]
    assert main(["--root", str(root), "specs", "validate"]) == 0
