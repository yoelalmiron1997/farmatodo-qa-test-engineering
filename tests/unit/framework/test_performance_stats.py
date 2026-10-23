"""Estadística de performance y baseline (TC-FW-005)."""

from __future__ import annotations

import pytest

from farmatodo_qa.metrics.performance import BaselineStatus, compare, compute_baseline, describe


@pytest.mark.case("TC-FW-005")
def test_descriptive_statistics() -> None:
    stats = describe([100, 120, 110, 130, 90])
    assert (stats.n, stats.minimum, stats.median, stats.maximum) == (5, 90, 110, 130)
    assert stats.mean == pytest.approx(110)
    assert stats.stdev == pytest.approx(15.811, rel=1e-3)
    assert stats.p95 is None
    assert any("P95 no disponible" in w for w in stats.warnings)


@pytest.mark.case("TC-FW-005")
def test_single_sample_has_no_stdev() -> None:
    stats = describe([42.0])
    assert stats.stdev is None
    assert stats.median == 42.0


@pytest.mark.case("TC-FW-005")
def test_no_samples() -> None:
    assert describe([]).n == 0
    assert describe([]).median is None


@pytest.mark.case("TC-FW-005")
@pytest.mark.parametrize(("n", "has_p95"), [(19, False), (20, True)])
def test_p95_requires_twenty_samples(n: int, has_p95: bool) -> None:
    stats = describe([float(i) for i in range(1, n + 1)])
    assert (stats.p95 is not None) is has_p95
    if has_p95:
        assert stats.p95 == 19.0  # rango más cercano


@pytest.mark.case("TC-FW-005")
def test_baseline_needs_five_runs() -> None:
    assert compute_baseline([100, 110, 120, 130]) is None
    assert compute_baseline([100, 110, 120, 130, 140, 999]) == 120


@pytest.mark.case("TC-FW-005")
@pytest.mark.parametrize(
    ("current", "baseline", "status"),
    [
        (None, 100.0, BaselineStatus.COLLECTING),
        (500.0, None, BaselineStatus.COLLECTING),
        (140.0, 100.0, BaselineStatus.OK),  # +40 %: debajo del umbral relativo
        (260.0, 100.0, BaselineStatus.OK),  # +160 % pero solo +160 ms: debajo del umbral absoluto
        (1700.0, 1000.0, BaselineStatus.ALERT),  # +70 % y +700 ms
        (1400.0, 1000.0, BaselineStatus.OK),  # +40 %
        (1600.0, 1000.0, BaselineStatus.ALERT),  # +60 % y +600 ms
    ],
    ids=[
        "sin-medicion",
        "sin-baseline",
        "relativo-bajo",
        "absoluto-bajo",
        "alerta-70",
        "relativo-40",
        "alerta-60",
    ],
)
def test_alert_requires_both_relative_and_absolute_change(
    current: float | None, baseline: float | None, status: BaselineStatus
) -> None:
    assert compare(current, baseline).status is status
