"""Esquema de resultados y normalización desde registros crudos (TC-FW-006)."""

from __future__ import annotations

import json
from datetime import timedelta
from typing import Any

import pytest
from pydantic import ValidationError

from farmatodo_qa.results.models import Environment, FailureCategory, FinalStatus, RunInfo, RunResult
from farmatodo_qa.results.normalizer import CatalogEntry, build_run_result
from farmatodo_qa.results.sanitize import sanitize
from support.factories import T0, O, case, run

CATALOG = {
    "TC-WC-001": CatalogEntry("TC-WC-001", "Palabras", "P0", "e2e", "functional", True, "h1"),
    "TC-WC-002": CatalogEntry("TC-WC-002", "Caracteres", "P0", "e2e", "functional", True, "h2"),
    "TC-PERF-001": CatalogEntry("TC-PERF-001", "Navegación", "P2", "e2e", "performance", True, "h3"),
    "TC-UX-001": CatalogEntry("TC-UX-001", "Manual", "P1", "manual", "exploratory", False, "h4"),
}
RUN = RunInfo(
    run_id="9",
    workflow="functional-tests",
    scope="functional",
    trigger="push",
    commit_sha="abc",
    started_at=T0,
    finished_at=T0 + timedelta(minutes=1),
)
ENV = Environment(kind="local", os="linux", python="3.12")


def record(
    nodeid: str, attempt: int, outcome: str, case_id: str | None = "TC-WC-001", **extra: Any
) -> dict[str, Any]:
    return {
        "nodeid": nodeid,
        "case_id": case_id,
        "param_id": None,
        "attempt": attempt,
        "outcome": outcome,
        "duration_s": 0.5,
        **extra,
    }


@pytest.mark.case("TC-FW-006")
def test_valid_result_round_trips_through_json() -> None:
    original = run([case("TC-WC-001", (O.FAILED, O.PASSED))])
    assert RunResult.model_validate_json(original.model_dump_json()) == original


@pytest.mark.case("TC-FW-006")
def test_unknown_schema_version_is_rejected() -> None:
    data = json.loads(run([case("TC-WC-001", (O.PASSED,))]).model_dump_json())
    data["schema_version"] = 2
    with pytest.raises(ValidationError, match="schema_version"):
        RunResult.model_validate(data)


@pytest.mark.case("TC-FW-006")
@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("cases", 0, "case_id"), "sin-formato"),
        (("run", "started_at"), "ayer"),
        (("cases", 0, "priority"), "P7"),
    ],
)
def test_invalid_fields_report_their_location(path: tuple[Any, ...], value: Any) -> None:
    data = json.loads(run([case("TC-WC-001", (O.PASSED,))]).model_dump_json())
    target = data
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(ValidationError) as excinfo:
        RunResult.model_validate(data)
    assert str(path[-1]) in str(excinfo.value)


@pytest.mark.case("TC-FW-006")
def test_normalizer_classifies_attempts_and_marks_not_run() -> None:
    records = [
        record("t::a", 1, "failed", exception_type="TimeoutException", message="timeout"),
        record("t::a", 2, "passed"),
    ]
    result, issues = build_run_result(records, CATALOG, RUN, ENV)
    assert issues == []
    by_id = {c.case_id: c for c in result.cases}
    assert by_id["TC-WC-001"].final_status is FinalStatus.FLAKY
    assert by_id["TC-WC-001"].executions[0].attempts[0].category is FailureCategory.TIMEOUT
    assert by_id["TC-WC-002"].final_status is FinalStatus.NOT_RUN
    assert "TC-PERF-001" not in by_id
    assert "TC-UX-001" not in by_id


@pytest.mark.case("TC-FW-006")
def test_results_without_case_id_are_reported_not_silently_dropped() -> None:
    _, issues = build_run_result(
        [record("t::x", 1, "passed", case_id=None), record("t::y", 1, "passed", case_id="TC-XX-999")],
        CATALOG,
        RUN,
        ENV,
    )
    assert [i.code for i in issues] == ["RES001", "RES002"]


@pytest.mark.case("TC-FW-006")
def test_blocked_records_keep_reason_and_category() -> None:
    result, _ = build_run_result([record("t::a", 1, "blocked", blocked_reason="HTTP 503")], CATALOG, RUN, ENV)
    execution = result.cases[0].executions[0]
    assert execution.final_status is FinalStatus.BLOCKED
    assert execution.blocked_reason == "HTTP 503"
    assert execution.attempts[0].category is FailureCategory.EXTERNAL_DEPENDENCY


@pytest.mark.case("TC-FW-006")
def test_secrets_are_redacted() -> None:
    text = "token=abc123 Authorization: Bearer xyz ghp_" + "a" * 30
    cleaned = sanitize(text) or ""
    assert "abc123" not in cleaned
    assert "ghp_" not in cleaned
    assert "xyz" not in cleaned


@pytest.mark.case("TC-FW-006")
def test_levels_limit_which_cases_count_as_not_run() -> None:
    catalog = {
        **CATALOG,
        "TC-ALG-001": CatalogEntry("TC-ALG-001", "Golden", "P0", "unit", "functional", True, "h5"),
    }
    result, _ = build_run_result([], catalog, RUN, ENV, levels=frozenset({"e2e"}))
    assert {c.case_id for c in result.cases} == {"TC-WC-001", "TC-WC-002"}
