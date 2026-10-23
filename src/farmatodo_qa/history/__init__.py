"""Persistencia del historial de corridas (SDD Anexo G)."""

from farmatodo_qa.history.repository import (
    DuplicateRunError,
    FileSystemHistoryRepository,
    HistoryReader,
    HistoryWriter,
    InMemoryHistoryRepository,
)

__all__ = [
    "DuplicateRunError",
    "FileSystemHistoryRepository",
    "HistoryReader",
    "HistoryWriter",
    "InMemoryHistoryRepository",
]
