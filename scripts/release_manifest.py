"""Congela el ambiente de un release: manifiesto JSON + notas en Markdown.

Lo ejecuta el workflow `release` después de validar la versión. Solo usa la biblioteca estándar.

    python scripts/release_manifest.py --tag v1.0.0 --run reports/run-result.json --out-dir dist
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPO = os.environ.get("GITHUB_REPOSITORY", "yoelalmiron1997/farmatodo-qa-test-engineering")
PORTAL = "https://{owner}.github.io/{name}/".format(owner=REPO.split("/")[0], name=REPO.split("/")[1])
_USES = re.compile(r"uses:\s*([\w.-]+/[\w.-]+)@([0-9a-f]{40})\s*#\s*(\S+)")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pinned_actions() -> dict[str, dict[str, str]]:
    actions: dict[str, dict[str, str]] = {}
    for workflow in sorted((ROOT / ".github/workflows").glob("*.yml")):
        for name, sha, tag in _USES.findall(workflow.read_text(encoding="utf-8")):
            actions[name] = {"version": tag, "sha": sha}
    return dict(sorted(actions.items()))


def locked_packages() -> dict[str, str]:
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    return {pkg["name"]: pkg.get("version", "") for pkg in lock.get("package", [])}


def build_manifest(tag: str, run: dict[str, Any], dist: Path) -> dict[str, Any]:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    env = run["environment"]
    packages = locked_packages()
    return {
        "release": tag,
        "project_version": project["version"],
        "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "commit": os.environ.get("GITHUB_SHA", run["run"].get("commit_sha")),
        "validation_run": run["run"]["run_url"],
        "runner": {
            # Nombres exactos que define el runner de GitHub (Linux distingue mayúsculas).
            "image": os.environ.get("ImageOS"),  # noqa: SIM112
            "image_version": os.environ.get("ImageVersion"),  # noqa: SIM112
            "os": os.environ.get("RUNNER_OS"),
            "arch": os.environ.get("RUNNER_ARCH"),
        },
        "toolchain": {
            "python": env["python"],
            "python_pin": (ROOT / ".python-version").read_text(encoding="utf-8").strip(),
            "uv": os.environ.get("UV_VERSION_USED", "").removeprefix("uv ").split(" ")[0] or None,
            "pytest": env["pytest"],
            "selenium": env["selenium"],
            "browser": env["browser"],
        },
        "lockfile": {"file": "uv.lock", "sha256": sha256(ROOT / "uv.lock"), "packages": packages},
        "github_actions": pinned_actions(),
        "results": {"summary": run["summary"], "gate": run["gate"]},
        "artifacts": {p.name: sha256(p) for p in sorted(dist.iterdir()) if p.is_file()},
    }


def render_notes(manifest: dict[str, Any], static_notes: str) -> str:
    s = manifest["results"]["summary"]
    tc = manifest["toolchain"]
    browser = tc["browser"]
    runner = manifest["runner"]
    tag = manifest["release"]
    gate = manifest["results"]["gate"]["decision"].upper()
    counts = " | ".join(str(s[k]) for k in ("executed", "passed", "flaky", "failed", "skipped", "blocked"))
    rows = "\n".join(
        f"| `{n}` | {a['version']} | `{a['sha'][:12]}` |" for n, a in manifest["github_actions"].items()
    )
    return f"""{static_notes.strip()}

## Validación de esta versión

La versión se validó completa antes de publicarse: [corrida de validación]({manifest["validation_run"]}).

| Ejecutados | PASS | FLAKY | FAIL | SKIPPED | BLOCKED | Quality gate |
|---|---|---|---|---|---|---|
| {counts} | **{gate}** |

Resultados en vivo: [portal de calidad]({PORTAL}) · [Test Execution]({PORTAL}generated/execution.html)

## Ambiente congelado

| Componente | Versión |
|---|---|
| Commit | `{manifest["commit"]}` |
| Runner | {runner["image"]} · imagen {runner["image_version"]} · {runner["arch"]} |
| Python | {tc["python"]} (fijado en `.python-version`: {tc["python_pin"]}) |
| uv | {tc["uv"]} |
| pytest · Selenium | {tc["pytest"]} · {tc["selenium"]} |
| Navegador | {browser["name"]} {browser["version"]} · driver {browser["driver_version"]} · headless · {browser["viewport"]} |
| Dependencias | `uv.lock` · sha256 `{manifest["lockfile"]["sha256"][:16]}…` · {len(manifest["lockfile"]["packages"])} paquetes |

<details><summary>Acciones de GitHub fijadas por SHA</summary>

| Acción | Versión | SHA |
|---|---|---|
{rows}

</details>

El detalle completo (todas las dependencias con su versión y el sha256 de cada archivo publicado) está en `environment.json`.

## Cómo reproducir esta versión

```bash
git clone https://github.com/{REPO}.git
cd {REPO.split("/")[1]}
git checkout {tag}
uv sync --frozen --group dev                       # Python {tc["python_pin"]} y las dependencias exactas de uv.lock
uv run word-frequency data/samples/farmatodo_example.txt
uv run pytest                                      # unit + integración
QA_BROWSER_VERSION={browser["version"]} uv run pytest tests/e2e --reruns 2 --qa-results-dir reports
```

`QA_BROWSER_VERSION` le pide a Selenium Manager esa versión exacta de Chrome (Chrome for Testing) y su driver. También se
puede reproducir en GitHub: *Actions → functional-tests → Run workflow* con `browser_version` = `{browser["version"]}`.
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--notes-out", type=Path, required=True)
    args = parser.parse_args(argv)

    project_version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"][
        "version"
    ]
    if args.tag.removeprefix("v") != project_version:
        print(
            f"el tag {args.tag} no coincide con la versión de pyproject.toml ({project_version})",
            file=sys.stderr,
        )
        return 1
    static = ROOT / "release-notes" / f"{args.tag}.md"
    if not static.is_file():
        print(f"faltan las notas del release: {static.relative_to(ROOT)}", file=sys.stderr)
        return 1

    run = json.loads(args.run.read_text(encoding="utf-8"))
    manifest = build_manifest(args.tag, run, args.out_dir)
    (args.out_dir / "environment.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    args.notes_out.write_text(render_notes(manifest, static.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"environment.json y notas generadas para {args.tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
