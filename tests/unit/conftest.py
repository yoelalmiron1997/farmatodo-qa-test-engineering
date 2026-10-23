"""La suite unitaria corre sin red: cualquier intento de abrir un socket falla (aislamiento verificable)."""

from __future__ import annotations

import pytest
import pytest_socket


@pytest.fixture(autouse=True)
def _no_network() -> None:
    pytest_socket.disable_socket(allow_unix_socket=True)
