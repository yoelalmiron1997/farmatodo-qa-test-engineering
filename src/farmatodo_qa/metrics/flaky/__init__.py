"""Detección y análisis de inestabilidad (SDD Anexo C)."""

from farmatodo_qa.metrics.flaky.classifier import aggregate_statuses, classify_attempts
from farmatodo_qa.metrics.flaky.failure_categories import DEFAULT_RULES, CategoryRule, categorize
from farmatodo_qa.metrics.flaky.history_analysis import StabilityStats, analyze_stability, top_unstable

__all__ = [
    "DEFAULT_RULES",
    "CategoryRule",
    "StabilityStats",
    "aggregate_statuses",
    "analyze_stability",
    "categorize",
    "classify_attempts",
    "top_unstable",
]
