"""Esperas explícitas sin ``time.sleep``.

``poll_until`` devuelve el último valor leído en lugar de lanzar ``TimeoutException``: así el
test hace la aserción con un mensaje esperado/actual y el fallo se categoriza como
*assertion* (el valor fue incorrecto) y no como *timeout*.
"""

from __future__ import annotations

import time
from collections.abc import Callable


def poll_until[T](
    read: Callable[[], T],
    predicate: Callable[[T], bool],
    timeout_s: float,
    interval_s: float = 0.05,
    stable_reads: int = 1,
) -> T:
    """Lee hasta que ``predicate`` sea verdadero en ``stable_reads`` lecturas seguidas o venza el plazo."""
    deadline = time.monotonic() + timeout_s
    value = read()
    hits = 1 if predicate(value) else 0
    while hits < stable_reads or not predicate(value):
        if time.monotonic() >= deadline:
            return value
        time.sleep(interval_s)  # intervalo de sondeo, no espera fija
        value = read()
        hits = hits + 1 if predicate(value) else 0
    return value
