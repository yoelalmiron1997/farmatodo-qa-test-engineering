"""Recolección por intento: un registro por intento en ``<results-dir>/attempts.jsonl``.

La recolección vive en una instancia (``QACollector``) registrada por sesión: no hay estado
global mutable.
"""

from __future__ import annotations

import json
import platform
import sys
from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from farmatodo_qa.pytest_plugin.blocked import blocked_reason
from farmatodo_qa.results.sanitize import sanitize

BROWSER_INFO_KEY = pytest.StashKey[dict[str, Any]]()


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("farmatodo-qa")
    group.addoption(
        "--qa-results-dir", default=None, help="directorio donde escribir attempts.jsonl y evidencias"
    )


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "case(id): vincula el test con un caso de specs/cases")
    if not config.pluginmanager.has_plugin("qa-collector"):
        config.pluginmanager.register(QACollector(config), "qa-collector")


def results_dir(config: pytest.Config) -> Path | None:
    value = config.getoption("--qa-results-dir", default=None)
    return Path(value) if value else None


def case_id_of(item: pytest.Item) -> str | None:
    marker = item.get_closest_marker("case")
    return str(marker.args[0]) if marker and marker.args else None


def param_id_of(nodeid: str) -> str | None:
    return nodeid[nodeid.index("[") + 1 : -1] if nodeid.endswith("]") and "[" in nodeid else None


def _skip_message(report: pytest.TestReport) -> str:
    return str(report.longrepr[2]) if isinstance(report.longrepr, tuple) else str(report.longrepr)


def _capture_evidence(item: pytest.Item, attempt: int) -> list[str]:
    out_dir = results_dir(item.config)
    driver = getattr(item, "funcargs", {}).get("driver")
    if out_dir is None or driver is None:
        return []
    stem = f"{case_id_of(item) or 'NO-CASE'}__{(param_id_of(item.nodeid) or 'default')[:60]}__a{attempt}"
    stem = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in stem)
    evidence_dir = out_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    saved: list[str] = []
    try:
        png = evidence_dir / f"{stem}.png"
        if driver.save_screenshot(str(png)):
            saved.append(f"evidence/{png.name}")
        html = evidence_dir / f"{stem}.html"
        html.write_text(driver.page_source, encoding="utf-8")
        saved.append(f"evidence/{html.name}")
    except Exception as exc:
        item.user_properties.append(("qa_evidence_error", repr(exc)))
    return saved


class QACollector:
    def __init__(self, config: pytest.Config) -> None:
        self.config = config
        self.records: list[dict[str, Any]] = []
        self.started_at = datetime.now(UTC)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(
        self, item: pytest.Item, call: pytest.CallInfo[None]
    ) -> Generator[None, Any, None]:
        outcome = yield
        report: pytest.TestReport = outcome.get_result()
        attempt = int(getattr(item, "execution_count", 1))
        report.user_properties.append(("qa_attempt", attempt))
        report.user_properties.append(("qa_case_id", case_id_of(item)))
        if report.failed and call.excinfo is not None:
            report.user_properties.append(("qa_exception_type", call.excinfo.typename))
            report.user_properties.append(("qa_message", sanitize(str(call.excinfo.value))))
            if report.when in {"setup", "call"}:
                report.user_properties.append(("qa_evidence", _capture_evidence(item, attempt)))

    def _classify(self, report: pytest.TestReport) -> tuple[str | None, str | None]:
        if report.skipped and report.when in {"setup", "call"}:
            reason = blocked_reason(_skip_message(report))
            return ("blocked" if reason else "skipped"), reason
        if report.when in {"setup", "call"} and report.outcome in {"failed", "rerun"}:
            return "failed", None
        if report.when == "call" and report.passed:
            return "passed", None
        return None, None

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        props = {k: v for k, v in report.user_properties if isinstance(k, str) and k.startswith("qa_")}
        if report.when == "teardown" and report.failed:
            last = self.records[-1] if self.records else None
            if last and last["nodeid"] == report.nodeid and last["outcome"] == "passed":
                last.update(
                    outcome="failed",
                    phase="teardown",
                    exception_type=props.get("qa_exception_type"),
                    message=props.get("qa_message"),
                )
            return
        outcome, reason = self._classify(report)
        if outcome is None:
            return
        finished = datetime.now(UTC)
        self.records.append(
            {
                "nodeid": report.nodeid,
                "case_id": props.get("qa_case_id"),
                "param_id": param_id_of(report.nodeid),
                "attempt": props.get("qa_attempt", 1),
                "phase": report.when,
                "outcome": outcome,
                "duration_s": round(report.duration, 4),
                "started_at": (finished - timedelta(seconds=report.duration)).isoformat(),
                "exception_type": props.get("qa_exception_type"),
                "message": props.get("qa_message"),
                "evidence": props.get("qa_evidence", []),
                "blocked_reason": reason,
            }
        )

    def pytest_sessionfinish(self, session: pytest.Session, exitstatus: int) -> None:
        out_dir = results_dir(self.config)
        if out_dir is None:
            return
        out_dir.mkdir(parents=True, exist_ok=True)
        with (out_dir / "attempts.jsonl").open("a", encoding="utf-8") as handle:
            for record in self.records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        seed = getattr(self.config.option, "randomly_seed", None)
        session_info: dict[str, Any] = {
            "started_at": self.started_at.isoformat(),
            "finished_at": datetime.now(UTC).isoformat(),
            "python": platform.python_version(),
            "pytest": pytest.__version__,
            "os": f"{platform.system()} {platform.release()}",
            "exit_status": int(exitstatus),
            "argv": sys.argv[1:],
            "random_seed": seed if isinstance(seed, int) else None,
            "reruns": int(getattr(self.config.option, "reruns", 0) or 0),
            "browser": self.config.stash.get(BROWSER_INFO_KEY, None),
        }
        stamp = self.started_at.strftime("%Y%m%dT%H%M%S%f")
        (out_dir / f"session-{stamp}.json").write_text(
            json.dumps(session_info, ensure_ascii=False, indent=1), encoding="utf-8"
        )
