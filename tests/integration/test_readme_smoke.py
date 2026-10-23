"""El README documenta comandos reales que funcionan (TC-DEL-001).

El job `readme-smoke` de CI ejecuta esos mismos comandos en un runner limpio; este test
asegura que README y comandos no diverjan.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
README = (ROOT / "README.md").read_text(encoding="utf-8")
GOLDEN = "14 words\n99 characters\nfarmatodo: 6\ncuida: 3\nsalud: 2\ntu: 2\ntoda: 1\n"


@pytest.mark.case("TC-DEL-001")
@pytest.mark.parametrize(
    "command",
    [
        "uv sync --group dev",
        "uv run word-frequency data/samples/farmatodo_example.txt",
        "uv run pytest tests/unit",
        "uv run pytest tests/e2e",
        "uv run qa specs validate",
        "uv run mkdocs serve",
    ],
)
def test_readme_documents_command(command: str) -> None:
    assert command in README, f"el README no documenta: {command}"


@pytest.mark.case("TC-DEL-001")
def test_documented_algorithm_command_prints_pdf_example() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "farmatodo_qa.word_frequency", "data/samples/farmatodo_example.txt"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert completed.stdout == GOLDEN
