"""Categorización de fallos: observaciones técnicas, no diagnósticos (SDD Anexo C.4).

Las reglas son datos evaluados en orden (OCP): agregar una categoría no modifica la función.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from farmatodo_qa.results.models import FailureCategory


@dataclass(frozen=True, slots=True)
class CategoryRule:
    category: FailureCategory
    exception_names: frozenset[str] = frozenset()
    message_pattern: re.Pattern[str] | None = None

    def matches(self, exception_type: str | None, message: str | None) -> bool:
        name = (exception_type or "").rsplit(".", 1)[-1]
        if self.exception_names and name not in self.exception_names:
            return False
        if self.message_pattern is not None and not self.message_pattern.search(message or ""):
            return False
        return bool(self.exception_names or self.message_pattern)


DEFAULT_RULES: tuple[CategoryRule, ...] = (
    CategoryRule(FailureCategory.EXTERNAL_DEPENDENCY, frozenset({"BlockedPrecondition"})),
    CategoryRule(FailureCategory.STALE_ELEMENT, frozenset({"StaleElementReferenceException"})),
    CategoryRule(FailureCategory.ELEMENT_NOT_FOUND, frozenset({"NoSuchElementException"})),
    CategoryRule(FailureCategory.TIMEOUT, frozenset({"TimeoutException", "TimeoutError"})),
    CategoryRule(
        FailureCategory.BROWSER_DRIVER,
        frozenset({"SessionNotCreatedException", "InvalidSessionIdException", "NoSuchWindowException"}),
    ),
    CategoryRule(
        FailureCategory.NETWORK,
        frozenset({"WebDriverException", "URLError", "ConnectionError"}),
        re.compile(r"net::ERR_|Name or service not known|Connection (refused|reset)", re.IGNORECASE),
    ),
    CategoryRule(
        FailureCategory.BROWSER_DRIVER,
        frozenset({"WebDriverException"}),
        re.compile(r"chrome not reachable|crash|disconnected|unable to connect", re.IGNORECASE),
    ),
    CategoryRule(FailureCategory.ASSERTION, frozenset({"AssertionError"})),
)


def categorize(
    exception_type: str | None, message: str | None, rules: Sequence[CategoryRule] = DEFAULT_RULES
) -> FailureCategory:
    for rule in rules:
        if rule.matches(exception_type, message):
            return rule.category
    return FailureCategory.UNKNOWN
