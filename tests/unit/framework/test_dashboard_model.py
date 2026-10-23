"""Modelo del dashboard y generación del portal (TC-FW-007)."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pytest

from farmatodo_qa.metrics.flaky import analyze_stability, top_unstable
from farmatodo_qa.reporting.dashboard_model import build_dashboard
from farmatodo_qa.reporting.portal import NO_DATA, PortalContext, build_portal
from farmatodo_qa.results.models import PerformanceSeries
from support.factories import T0, O, case, run

ROOT = Path(__file__).resolve().parents[3]


def history(statuses: list[tuple[O, ...]], spec_hash: str = "sha256:abc", offset: int = 0) -> list:
    return [
        run(
            [case("TC-WC-001", outcomes, spec_hash=spec_hash)],
            run_id=str(i + offset),
            started=T0 + timedelta(hours=i + offset),
        )
        for i, outcomes in enumerate(statuses)
    ]


@pytest.mark.case("TC-FW-007")
def test_empty_history_is_no_data_not_zeros() -> None:
    model = build_dashboard([], T0)
    assert not model.has_functional_data
    assert model.latest_functional is None
    assert model.trend == ()
    assert model.performance == ()


@pytest.mark.case("TC-FW-007")
def test_trend_and_case_history() -> None:
    runs = history([(O.PASSED,), (O.FAILED, O.PASSED), (O.FAILED, O.FAILED, O.FAILED)])
    model = build_dashboard(runs, T0)
    assert [p.run_key for p in model.trend] == ["0-1", "1-1", "2-1"]
    assert [v.status.value for v in model.case_history["TC-WC-001"]] == ["FAIL", "FLAKY", "PASS"]
    assert model.flaky_by_priority == {}


@pytest.mark.case("TC-FW-007")
def test_suspected_flaky_requires_alternation_in_comparable_runs() -> None:
    alternating = history([(O.PASSED,), (O.FAILED,), (O.PASSED,), (O.FAILED,), (O.PASSED,)])
    stats = analyze_stability(alternating)["TC-WC-001"]
    assert stats.n == 5
    assert stats.suspected
    assert stats.flip_rate == 1.0
    assert stats.stability == 0.6
    assert top_unstable([stats])[0].case_id == "TC-WC-001"


@pytest.mark.case("TC-FW-007")
def test_consistent_failure_is_not_flaky() -> None:
    failing = history([(O.PASSED,), (O.PASSED,), (O.FAILED,), (O.FAILED,), (O.FAILED,)])
    assert not analyze_stability(failing)["TC-WC-001"].suspected


@pytest.mark.case("TC-FW-007")
def test_runs_with_different_spec_are_not_comparable() -> None:
    runs = history([(O.FAILED,)] * 4, spec_hash="sha256:old") + history(
        [(O.PASSED,)], spec_hash="sha256:new", offset=10
    )
    stats = analyze_stability(runs)["TC-WC-001"]
    assert stats.n == 1
    assert not stats.suspected


@pytest.mark.case("TC-FW-007")
def test_performance_series_compare_against_baseline_after_five_runs() -> None:
    runs = [
        run(
            [],
            run_id=str(i),
            started=T0 + timedelta(days=i),
            scope="performance",
            performance=[PerformanceSeries(case_id="TC-PERF-002", series="end_to_end", samples=[ms] * 5)],
        )
        for i, ms in enumerate([100, 110, 90, 100, 105, 900])
    ]
    view = build_dashboard(runs, T0).performance[0]
    assert view.latest.median == 900
    assert view.comparison.baseline_ms == 100
    assert view.comparison.status.value == "alert"


@pytest.mark.case("TC-FW-007")
def test_portal_builds_with_and_without_history(tmp_path: Path) -> None:
    from farmatodo_qa.cli import Project

    project = Project(ROOT)
    for runs in ([], history([(O.FAILED, O.PASSED)])):
        out = tmp_path / f"out{len(runs)}"
        ctx = PortalContext(
            root=project.root,
            out_dir=out,
            repository="owner/repo",
            code_ref="abc",
            requirements=project.requirements,
            cases=project.cases,
            bugs=project.bugs,
            implementations=project.implementations,
            model=build_dashboard(runs, T0),
        )
        build_portal(ctx)
        dashboard = (out / "dashboard.md").read_text(encoding="utf-8")
        assert ("**Quality gate:**" in dashboard) is bool(runs)
        assert (dashboard.count(NO_DATA) == 3) is (not runs)  # estado, tendencia y performance
        assert (out / "cases" / "TC-WC-003.md").exists()
        assert "github.com/owner/repo/blob/abc/tests/" in (out / "traceability.md").read_text(
            encoding="utf-8"
        )
