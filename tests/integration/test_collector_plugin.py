"""El plugin registra cada intento, el Case ID y BLOCKED (TC-FW-010)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from farmatodo_qa.results.models import Environment, FinalStatus, RunInfo
from farmatodo_qa.results.normalizer import CatalogEntry, build_run_result

SYNTHETIC_SUITE = """
import pathlib
import pytest
from farmatodo_qa.pytest_plugin.blocked import block

COUNTER = pathlib.Path(__file__).with_name("counter.txt")

@pytest.fixture
def external_site():
    block("HTTP 503 en el probe previo")

@pytest.mark.case("TC-SY-001")
def test_passes():
    assert True

@pytest.mark.case("TC-SY-002")
def test_fails_then_passes():
    count = int(COUNTER.read_text()) if COUNTER.exists() else 0
    COUNTER.write_text(str(count + 1))
    assert count >= 1, "falla solo en el primer intento"

@pytest.mark.case("TC-SY-003")
def test_always_fails():
    assert 1 == 2, "esperado 2, actual 1"

@pytest.mark.case("TC-SY-004")
def test_blocked(external_site):
    assert True

def test_without_marker():
    assert True
"""


def _catalog() -> dict[str, CatalogEntry]:
    return {
        f"TC-SY-00{i}": CatalogEntry(f"TC-SY-00{i}", f"Sintético {i}", "P1", "e2e", "functional", True, "h")
        for i in range(1, 5)
    }


@pytest.mark.case("TC-FW-010")
def test_plugin_records_every_attempt_with_reruns(pytester: pytest.Pytester, tmp_path: Path) -> None:
    pytester.makepyfile(test_synthetic=SYNTHETIC_SUITE)
    out = tmp_path / "results"
    result = pytester.runpytest(
        "-p", "farmatodo_qa.pytest_plugin", "-p", "no:randomly", "--reruns", "2", "--qa-results-dir", str(out)
    )
    assert result.parseoutcomes() == {"passed": 3, "failed": 1, "skipped": 1, "rerun": 3}

    records = [json.loads(line) for line in (out / "attempts.jsonl").read_text().splitlines()]
    by_test: dict[str, list[dict]] = {}
    for record in records:
        by_test.setdefault(record["nodeid"].split("::")[-1], []).append(record)

    assert [r["outcome"] for r in by_test["test_passes"]] == ["passed"]
    assert [(r["attempt"], r["outcome"]) for r in by_test["test_fails_then_passes"]] == [
        (1, "failed"),
        (2, "passed"),
    ]
    assert [r["outcome"] for r in by_test["test_always_fails"]] == ["failed"] * 3
    assert by_test["test_always_fails"][0]["exception_type"] == "AssertionError"
    assert "esperado 2, actual 1" in by_test["test_always_fails"][0]["message"]
    assert by_test["test_blocked"][0]["outcome"] == "blocked"
    assert by_test["test_blocked"][0]["blocked_reason"] == "HTTP 503 en el probe previo"
    assert by_test["test_without_marker"][0]["case_id"] is None

    session = json.loads(next(out.glob("session-*.json")).read_text())
    assert session["reruns"] == 2

    now = datetime.now(UTC)
    run = RunInfo(
        run_id="1",
        workflow="t",
        scope="functional",
        trigger="local",
        commit_sha="x",
        started_at=now,
        finished_at=now,
    )
    normalized, issues = build_run_result(
        records, _catalog(), run, Environment(kind="local", os="x", python="3")
    )
    statuses = {c.case_id: c.final_status for c in normalized.cases}
    assert statuses == {
        "TC-SY-001": FinalStatus.PASS,
        "TC-SY-002": FinalStatus.FLAKY,
        "TC-SY-003": FinalStatus.FAIL,
        "TC-SY-004": FinalStatus.BLOCKED,
    }
    assert [i.code for i in issues] == ["RES001"]  # el test sin marker no se pierde en silencio
    assert normalized.summary.retries == 3


@pytest.mark.case("TC-FW-010")
def test_reruns_can_be_disabled(pytester: pytest.Pytester, tmp_path: Path) -> None:
    pytester.makepyfile(test_synthetic=SYNTHETIC_SUITE)
    out = tmp_path / "results"
    result = pytester.runpytest(
        "-p", "farmatodo_qa.pytest_plugin", "-p", "no:randomly", "--qa-results-dir", str(out)
    )
    result.assert_outcomes(passed=2, failed=2, skipped=1)
    records = [json.loads(line) for line in (out / "attempts.jsonl").read_text().splitlines()]
    assert all(r["attempt"] == 1 for r in records)
