"""Clasificación de intentos y categorías de fallo (TC-FW-001)."""

from __future__ import annotations

import pytest

from farmatodo_qa.metrics.flaky import aggregate_statuses, categorize, classify_attempts
from farmatodo_qa.metrics.flaky.failure_categories import CategoryRule
from farmatodo_qa.results.models import AttemptOutcome as O
from farmatodo_qa.results.models import FailureCategory, FinalStatus


@pytest.mark.case("TC-FW-001")
@pytest.mark.parametrize(
    ("outcomes", "expected"),
    [
        ([O.PASSED], FinalStatus.PASS),
        ([O.FAILED, O.PASSED], FinalStatus.FLAKY),
        ([O.FAILED, O.FAILED, O.PASSED], FinalStatus.FLAKY),
        ([O.FAILED, O.FAILED, O.FAILED], FinalStatus.FAIL),
        ([O.FAILED], FinalStatus.FAIL),
        ([O.SKIPPED], FinalStatus.SKIPPED),
        ([O.BLOCKED], FinalStatus.BLOCKED),
        ([], FinalStatus.NOT_RUN),
    ],
    ids=[
        "pass",
        "fail-pass",
        "fail-fail-pass",
        "fail-x3",
        "fail-sin-reintento",
        "skip",
        "blocked",
        "sin-intentos",
    ],
)
def test_attempt_sequence_classification(outcomes: list[O], expected: FinalStatus) -> None:
    assert classify_attempts(outcomes) is expected


@pytest.mark.case("TC-FW-001")
def test_flaky_is_never_reported_as_clean_pass() -> None:
    assert classify_attempts([O.FAILED, O.PASSED]) is not FinalStatus.PASS


@pytest.mark.case("TC-FW-001")
@pytest.mark.parametrize(
    ("statuses", "expected"),
    [
        ([FinalStatus.PASS, FinalStatus.FAIL], FinalStatus.FAIL),
        ([FinalStatus.PASS, FinalStatus.FLAKY], FinalStatus.FLAKY),
        ([FinalStatus.PASS, FinalStatus.BLOCKED], FinalStatus.BLOCKED),
        ([FinalStatus.PASS, FinalStatus.SKIPPED], FinalStatus.PASS),
        ([], FinalStatus.NOT_RUN),
    ],
)
def test_case_status_is_worst_execution(statuses: list[FinalStatus], expected: FinalStatus) -> None:
    assert aggregate_statuses(statuses) is expected


@pytest.mark.case("TC-FW-001")
@pytest.mark.parametrize(
    ("exc", "message", "expected"),
    [
        ("AssertionError", "esperado 9, actual 8", FailureCategory.ASSERTION),
        ("selenium.common.exceptions.TimeoutException", "", FailureCategory.TIMEOUT),
        ("NoSuchElementException", "", FailureCategory.ELEMENT_NOT_FOUND),
        ("StaleElementReferenceException", "", FailureCategory.STALE_ELEMENT),
        ("SessionNotCreatedException", "", FailureCategory.BROWSER_DRIVER),
        ("WebDriverException", "unknown error: net::ERR_NAME_NOT_RESOLVED", FailureCategory.NETWORK),
        ("WebDriverException", "chrome not reachable", FailureCategory.BROWSER_DRIVER),
        ("BlockedPrecondition", None, FailureCategory.EXTERNAL_DEPENDENCY),
        ("ValueError", "otra cosa", FailureCategory.UNKNOWN),
        (None, None, FailureCategory.UNKNOWN),
    ],
)
def test_failure_categories(exc: str | None, message: str | None, expected: FailureCategory) -> None:
    assert categorize(exc, message) is expected


@pytest.mark.case("TC-FW-001")
def test_categories_are_extensible_without_code_changes() -> None:
    rules = (CategoryRule(FailureCategory.NETWORK, frozenset({"MyProxyError"})),)
    assert categorize("MyProxyError", None, rules) is FailureCategory.NETWORK
