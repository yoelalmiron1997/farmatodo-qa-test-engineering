"""CLI del Ejercicio 4: ``word-frequency ARCHIVO [--histogram]``.

Códigos de salida: 0 éxito · 2 archivo inexistente o no legible · 3 contenido no UTF-8.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from farmatodo_qa.word_frequency.analyzer import analyze_lines
from farmatodo_qa.word_frequency.render import render_histogram, render_report

EXIT_OK = 0
EXIT_FILE_ERROR = 2
EXIT_DECODE_ERROR = 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="word-frequency",
        description="Cuenta palabras, caracteres (sin saltos de línea) y frecuencias de un archivo de texto.",
    )
    parser.add_argument("path", type=Path, help="archivo de texto UTF-8")
    parser.add_argument("--histogram", action="store_true", help="agrega un histograma de barras")
    parser.add_argument("--width", type=int, default=40, help="ancho máximo de las barras (por defecto 40)")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path: Path = args.path
    try:
        # utf-8-sig descarta el BOM, que no es contenido del texto.
        with path.open(encoding="utf-8-sig", newline="") as handle:
            stats = analyze_lines(handle)
    except (FileNotFoundError, IsADirectoryError, PermissionError) as exc:
        print(f"error: no se puede leer el archivo '{path}': {exc.strerror}", file=sys.stderr)
        return EXIT_FILE_ERROR
    except UnicodeDecodeError as exc:
        print(f"error: el archivo '{path}' no es UTF-8 válido (byte {exc.start})", file=sys.stderr)
        return EXIT_DECODE_ERROR

    sys.stdout.write(render_report(stats))
    if args.histogram and stats.frequencies:
        sys.stdout.write("\n" + render_histogram(stats.frequencies, width=args.width))
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
