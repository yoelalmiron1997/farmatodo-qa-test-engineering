"""Lectura de especificaciones desde disco (adaptador de I/O)."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import yaml

from farmatodo_qa.specs.models import BugReport, CaseFrontMatter, CaseSpec, ImplementationRef, Requirement
from farmatodo_qa.traceability.implementation_scan import scan_source


class SpecError(ValueError):
    """Archivo de especificación ilegible o con front matter inválido."""


def split_front_matter(text: str, source: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        raise SpecError(f"{source}: falta el front matter YAML inicial")
    try:
        _, front, body = text.split("---\n", 2)
    except ValueError as exc:
        raise SpecError(f"{source}: front matter sin cierre '---'") from exc
    data = yaml.safe_load(front) or {}
    if not isinstance(data, dict):
        raise SpecError(f"{source}: el front matter debe ser un mapa")
    return data, body


def load_requirements(path: Path) -> list[Requirement]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [Requirement.model_validate(item) for item in data["requirements"]]


def load_case(path: Path, root: Path) -> CaseSpec:
    text = path.read_text(encoding="utf-8")
    meta, body = split_front_matter(text, str(path))
    return CaseSpec(
        meta=CaseFrontMatter.model_validate(meta),
        body=body,
        path=path.relative_to(root).as_posix(),
        spec_hash="sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:16],
    )


def load_cases(cases_dir: Path, root: Path) -> list[CaseSpec]:
    return [load_case(path, root) for path in sorted(cases_dir.glob("TC-*.md"))]


def load_bugs(bugs_dir: Path, root: Path) -> list[BugReport]:
    bugs = []
    for path in sorted([*bugs_dir.glob("BUG-*.md"), *bugs_dir.glob("OBS-*.md")]):
        meta, _ = split_front_matter(path.read_text(encoding="utf-8"), str(path))
        meta["environment"] = {str(k): str(v) for k, v in (meta.get("environment") or {}).items()}
        bugs.append(BugReport.model_validate({**meta, "path": path.relative_to(root).as_posix()}))
    return bugs


def iter_test_files(tests_dir: Path) -> Iterable[Path]:
    for path in sorted(tests_dir.rglob("test_*.py")):
        if "__pycache__" not in path.parts:
            yield path


def scan_implementations(tests_dir: Path, root: Path) -> tuple[list[ImplementationRef], list[str]]:
    """Devuelve (referencias case→test, tests sin marker ``case``)."""
    refs: list[ImplementationRef] = []
    unmarked: list[str] = []
    for path in iter_test_files(tests_dir):
        rel = path.relative_to(root).as_posix()
        found, missing = scan_source(rel, path.read_text(encoding="utf-8"))
        refs.extend(found)
        unmarked.extend(missing)
    return refs, unmarked
