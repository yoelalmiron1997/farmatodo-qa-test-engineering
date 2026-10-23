"""Suite de contrato para ambas implementaciones del historial (TC-FW-003, LSP)."""

from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
from pathlib import Path

import pytest

from farmatodo_qa.history import DuplicateRunError, FileSystemHistoryRepository, InMemoryHistoryRepository
from farmatodo_qa.history.repository import HistoryReader, HistoryWriter
from support.factories import T0, O, case, run


class Repo(HistoryReader, HistoryWriter):  # type: ignore[misc]
    """Solo para tipado del parámetro."""


def _fs(tmp_path: Path) -> Repo:
    return FileSystemHistoryRepository(tmp_path / "history")  # type: ignore[return-value]


def _memory(_: Path) -> Repo:
    return InMemoryHistoryRepository()  # type: ignore[return-value]


IMPLEMENTATIONS = pytest.mark.parametrize("make_repo", [_fs, _memory], ids=["filesystem", "memoria"])


@pytest.mark.case("TC-FW-003")
@IMPLEMENTATIONS
def test_empty_history_returns_empty_list(make_repo: Callable[[Path], Repo], tmp_path: Path) -> None:
    assert make_repo(tmp_path).load_runs() == []


@pytest.mark.case("TC-FW-003")
@IMPLEMENTATIONS
def test_runs_are_returned_in_chronological_order(make_repo: Callable[[Path], Repo], tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    late = run([case("TC-WC-001", (O.PASSED,))], run_id="2", started=T0 + timedelta(days=1))
    early = run([case("TC-WC-001", (O.FAILED,))], run_id="1", started=T0)
    repo.save_run(late)
    repo.save_run(early)
    assert [r.run.run_id for r in repo.load_runs()] == ["1", "2"]
    assert repo.load_runs()[0] == early


@pytest.mark.case("TC-FW-003")
@IMPLEMENTATIONS
def test_same_run_is_never_overwritten(make_repo: Callable[[Path], Repo], tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    original = run([case("TC-WC-001", (O.PASSED,))], run_id="7")
    repo.save_run(original)
    with pytest.raises(DuplicateRunError):
        repo.save_run(run([case("TC-WC-001", (O.FAILED,))], run_id="7"))
    assert repo.load_runs() == [original]


@pytest.mark.case("TC-FW-003")
def test_filesystem_layout_is_partitioned_by_workflow_and_month(tmp_path: Path) -> None:
    repo = FileSystemHistoryRepository(tmp_path)
    rel = repo.save_run(run([case("TC-WC-001", (O.PASSED,))], run_id="42"))
    assert rel == "runs/functional-tests/2026/10/42-1.json"
    assert repo.load_runs(workflow="performance") == []
