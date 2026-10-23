"""Indicadores y denominadores (TC-FW-002)."""

from __future__ import annotations

import pytest

from farmatodo_qa.results.models import FinalStatus
from support.factories import O, case, run


@pytest.mark.case("TC-FW-002")
def test_summary_counts_cases_and_attempts_separately() -> None:
    cases = [
        *[case(f"TC-WC-00{i}", (O.PASSED,)) for i in range(1, 7)],
        case("TC-WC-007", (O.FAILED, O.PASSED)),
        case("TC-WC-008", (O.FAILED, O.PASSED)),
        case("TC-WC-009", (O.FAILED, O.FAILED, O.FAILED)),
        case("TC-WC-010", (O.BLOCKED,)),
    ]
    s = run(cases).summary
    assert (s.specified, s.executed) == (10, 9)
    assert (s.passed, s.flaky, s.failed, s.blocked, s.skipped, s.not_run) == (6, 2, 1, 1, 0, 0)
    assert (s.attempts, s.retries, s.cases_with_retries) == (13, 4, 3)
    assert s.flaky_rate == pytest.approx(2 / 9)
    assert s.first_attempt_pass_rate == pytest.approx(6 / 9)
    assert s.final_pass_rate == pytest.approx(8 / 9)
    assert s.mean_case_duration_s == pytest.approx(13 / 9)
    assert s.failures_by_category == {"assertion": 5}


@pytest.mark.case("TC-FW-002")
def test_rates_are_none_without_executions() -> None:
    s = run([case("TC-WC-001", (O.BLOCKED,)), case("TC-WC-002")]).summary
    assert s.executed == 0
    assert s.flaky_rate is None
    assert s.first_attempt_pass_rate is None
    assert s.final_pass_rate is None
    assert s.not_run == 1


@pytest.mark.case("TC-FW-002")
def test_parametrized_case_counts_once_with_worst_status() -> None:
    c = case("TC-WC-001", (O.PASSED,), (O.FAILED, O.PASSED), (O.PASSED,))
    assert c.final_status is FinalStatus.FLAKY
    s = run([c]).summary
    assert (s.executed, s.flaky, s.attempts, s.retries, s.cases_with_retries) == (1, 1, 4, 1, 1)
