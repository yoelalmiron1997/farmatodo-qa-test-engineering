"""Estadística descriptiva de performance y comparación con baseline (SDD Anexo D)."""

from farmatodo_qa.metrics.performance.baseline import (
    BaselineComparison,
    BaselineStatus,
    compare,
    compute_baseline,
)
from farmatodo_qa.metrics.performance.stats import PerfStats, describe

__all__ = ["BaselineComparison", "BaselineStatus", "PerfStats", "compare", "compute_baseline", "describe"]
