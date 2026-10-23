"""Estado BLOCKED (SDD §5.6): precondición externa fallida verificada *antes* del cuerpo del test."""

from __future__ import annotations

from typing import NoReturn

import pytest

BLOCKED_PREFIX = "BLOCKED: "


def block(reason: str) -> NoReturn:
    """Marca el test como BLOCKED. Pytest lo ve como skip (no como pass); el modelo lo distingue."""
    pytest.skip(BLOCKED_PREFIX + reason)


def blocked_reason(skip_message: str) -> str | None:
    marker = skip_message.find(BLOCKED_PREFIX)
    return skip_message[marker + len(BLOCKED_PREFIX) :].strip() if marker >= 0 else None
