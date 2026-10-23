"""Contratos de historial (ISP: lectura y escritura separadas) e implementaciones intercambiables (LSP)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol

from farmatodo_qa.results.models import RunResult


class DuplicateRunError(FileExistsError):
    """Ya existe un registro para (workflow, run_id, run_attempt): nunca se sobrescribe."""


class HistoryReader(Protocol):
    def load_runs(self, workflow: str | None = None) -> list[RunResult]: ...


class HistoryWriter(Protocol):
    def save_run(self, run: RunResult) -> str: ...


class InMemoryHistoryRepository:
    def __init__(self) -> None:
        self._runs: dict[str, RunResult] = {}

    def save_run(self, run: RunResult) -> str:
        key = f"{run.run.workflow}/{run.key}"
        if key in self._runs:
            raise DuplicateRunError(key)
        self._runs[key] = run
        return key

    def load_runs(self, workflow: str | None = None) -> list[RunResult]:
        runs = [r for r in self._runs.values() if workflow is None or r.run.workflow == workflow]
        return sorted(runs, key=lambda r: r.run.started_at)


class FileSystemHistoryRepository:
    """``runs/<workflow>/<YYYY>/<MM>/<run_id>-<run_attempt>.json``; archivos inmutables."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def path_for(self, run: RunResult) -> Path:
        started = run.run.started_at
        return self.root / "runs" / run.run.workflow / f"{started:%Y}" / f"{started:%m}" / f"{run.key}.json"

    def save_run(self, run: RunResult) -> str:
        path = self.path_for(run)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            # O_EXCL: la creación falla de forma atómica si otro proceso ya escribió el registro.
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        except FileExistsError as exc:
            raise DuplicateRunError(str(path)) from exc
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(run.model_dump_json(indent=1))
        return path.relative_to(self.root).as_posix()

    def load_runs(self, workflow: str | None = None) -> list[RunResult]:
        base = self.root / "runs"
        if workflow is not None:
            base = base / workflow
        if not base.exists():
            return []
        runs = [RunResult.model_validate_json(p.read_text(encoding="utf-8")) for p in base.rglob("*.json")]
        return sorted(runs, key=lambda r: r.run.started_at)
