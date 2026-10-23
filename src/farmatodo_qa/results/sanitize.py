"""Redacción de secretos antes de persistir mensajes de error (SDD Anexo F.3)."""

from __future__ import annotations

import re

_PATTERNS = (
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]+"),
    re.compile(r"(?i)(authorization|token|password|secret|api[_-]?key)\s*[:=]\s*(bearer\s+)?\S+"),
)


def sanitize(text: str | None, limit: int = 4000) -> str | None:
    if text is None:
        return None
    for pattern in _PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text[:limit]
