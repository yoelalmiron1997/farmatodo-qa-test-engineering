"""Descubrimiento estático de ``@pytest.mark.case("TC-...")`` mediante AST.

No importa los tests (no necesita pytest ni Selenium): lee el código fuente como datos.
Reconoce el marker en decoradores de funciones y clases, en ``pytestmark`` de módulo y
en ``pytest.param(..., marks=pytest.mark.case(...))``.
"""

from __future__ import annotations

import ast

from farmatodo_qa.specs.models import ImplementationRef


def _case_ids_in(node: ast.AST) -> list[str]:
    ids: list[str] = []
    for sub in ast.walk(node):
        if (
            isinstance(sub, ast.Call)
            and isinstance(sub.func, ast.Attribute)
            and sub.func.attr == "case"
            and sub.args
            and isinstance(sub.args[0], ast.Constant)
            and isinstance(sub.args[0].value, str)
        ):
            ids.append(sub.args[0].value)
    return ids


def _module_marks(tree: ast.Module) -> list[str]:
    ids: list[str] = []
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "pytestmark" for t in stmt.targets
        ):
            ids.extend(_case_ids_in(stmt.value))
    return ids


def scan_source(path: str, source: str) -> tuple[list[ImplementationRef], list[str]]:
    tree = ast.parse(source, filename=path)
    module_ids = _module_marks(tree)
    refs: list[ImplementationRef] = []
    unmarked: list[str] = []

    def visit_function(fn: ast.FunctionDef | ast.AsyncFunctionDef, inherited: list[str]) -> None:
        if not fn.name.startswith("test"):
            return
        ids = list(inherited)
        for decorator in fn.decorator_list:
            ids.extend(_case_ids_in(decorator))
        if not ids:
            unmarked.append(f"{path}::{fn.name}")
        refs.extend(
            ImplementationRef(case_id=cid, path=path, line=fn.lineno, test_name=fn.name)
            for cid in dict.fromkeys(ids)
        )

    for stmt in tree.body:
        if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef):
            visit_function(stmt, module_ids)
        elif isinstance(stmt, ast.ClassDef) and stmt.name.startswith("Test"):
            class_ids = module_ids + [cid for d in stmt.decorator_list for cid in _case_ids_in(d)]
            for item in stmt.body:
                if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                    visit_function(item, class_ids)
    return refs, unmarked
