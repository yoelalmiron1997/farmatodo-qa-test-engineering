"""CLI ``qa``: composition root. Une adaptadores (disco, git, entorno) con el núcleo puro.

Subcomandos:
  qa specs validate          valida specs, trazabilidad y bloques generados del SDD
  qa specs generate [--check] regenera los bloques generados del SDD
  qa results build           attempts.jsonl → run-result.json (normalizado + gate)
  qa results schema          imprime el JSON Schema del resultado
  qa report summary          reporte resumen (Markdown/HTML, Job Summary)
  qa gate                    evalúa el quality gate (código de salida = estado del job)
  qa history save            agrega una corrida al historial (nunca sobrescribe)
  qa portal build            genera las páginas del portal en docs/generated
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

import yaml

from farmatodo_qa.history import DuplicateRunError, FileSystemHistoryRepository
from farmatodo_qa.quality_gate import GatePolicy, default_policy, evaluate, exit_code
from farmatodo_qa.reporting.dashboard_model import build_dashboard
from farmatodo_qa.reporting.portal import PortalContext, build_portal
from farmatodo_qa.reporting.summary import render_html, render_markdown
from farmatodo_qa.results.models import BrowserInfo, Environment, PerformanceSeries, RunInfo, RunResult
from farmatodo_qa.results.normalizer import CatalogEntry, build_run_result
from farmatodo_qa.specs.loader import load_bugs, load_cases, load_requirements, scan_implementations
from farmatodo_qa.specs.models import BugReport, CaseSpec, ImplementationRef, Requirement
from farmatodo_qa.specs.validator import Issue, validate
from farmatodo_qa.traceability.catalog import (
    catalog_summary,
    implemented_ids,
    render_inventory,
    render_traceability,
    replace_generated_block,
)

SDD_BLOCKS = ("summary", "inventory", "traceability")


# --------------------------------------------------------------------------- carga


class Project:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.requirements: list[Requirement] = load_requirements(
            self.root / "specs/requirements/requirements.yaml"
        )
        self.cases: list[CaseSpec] = load_cases(self.root / "specs/cases", self.root)
        self.bugs: list[BugReport] = (
            load_bugs(self.root / "docs/bugs", self.root) if (self.root / "docs/bugs").exists() else []
        )
        self.implementations: list[ImplementationRef]
        self.unmarked: list[str]
        self.implementations, self.unmarked = scan_implementations(self.root / "tests", self.root)

    def catalog(self) -> dict[str, CatalogEntry]:
        return {
            c.id: CatalogEntry(
                case_id=c.id,
                title=c.meta.title,
                priority=c.meta.priority,
                level=c.meta.level,
                test_type=c.meta.test_type,
                automated=c.is_automated,
                spec_hash=c.spec_hash,
                known_defect=c.meta.known_defect,
            )
            for c in self.cases
        }

    def generated_blocks(self) -> dict[str, str]:
        impl = implemented_ids(self.implementations)
        return {
            "summary": catalog_summary(self.cases, self.requirements),
            "inventory": render_inventory(self.cases, impl),
            "traceability": render_traceability(self.requirements, self.cases),
        }

    def render_sdd(self) -> tuple[str, str]:
        path = self.root / "specs/SDD.md"
        current = path.read_text(encoding="utf-8")
        updated = current
        for name, content in self.generated_blocks().items():
            updated = replace_generated_block(updated, name, content)
        return current, updated


# --------------------------------------------------------------------------- specs


def cmd_specs_validate(args: argparse.Namespace) -> int:
    project = Project(Path(args.root))
    existing = frozenset(
        p.relative_to(project.root).as_posix() for p in (project.root / "tests").rglob("*.py")
    )
    issues = validate(
        project.requirements,
        project.cases,
        project.implementations,
        project.unmarked,
        bugs=project.bugs,
        existing_paths=existing,
    )
    current, updated = project.render_sdd()
    if current != updated:
        issues.append(
            Issue(
                "GEN001",
                "bloques generados del SDD desactualizados: ejecutar `qa specs generate`",
                "specs/SDD.md",
            )
        )
    for issue in issues:
        print(issue)
    print(
        f"{len(project.requirements)} requisitos · {len(project.cases)} casos · "
        f"{len(project.implementations)} vínculos case→test · {len(project.bugs)} reportes de defecto · "
        f"{len(issues)} problema(s)"
    )
    return 1 if issues else 0


def cmd_specs_generate(args: argparse.Namespace) -> int:
    project = Project(Path(args.root))
    current, updated = project.render_sdd()
    if args.check:
        if current != updated:
            print("GEN001: bloques generados del SDD desactualizados", file=sys.stderr)
            return 1
        print("SDD al día")
        return 0
    (project.root / "specs/SDD.md").write_text(updated, encoding="utf-8")
    print("SDD actualizado" if current != updated else "SDD sin cambios")
    return 0


# --------------------------------------------------------------------------- results


def _git_sha(root: Path) -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _sessions(results: Path) -> list[dict[str, Any]]:
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(results.glob("session-*.json"))]


def _performance(results: Path) -> list[PerformanceSeries]:
    out = []
    for entry in _read_jsonl(results / "performance.jsonl"):
        out.append(
            PerformanceSeries(
                case_id=entry["case_id"],
                series=entry["series"],
                samples=entry.get("samples", []),
                invalid_samples=int(entry.get("invalid_samples", 0)),
                warmup_discarded=int(entry.get("warmup_discarded", 0)),
                poll_resolution_ms=entry.get("poll_resolution_ms"),
            )
        )
    return out


def load_policy(path: Path) -> GatePolicy:
    if path.exists():
        return GatePolicy.from_mapping(yaml.safe_load(path.read_text(encoding="utf-8")))
    return default_policy()


def cmd_results_build(args: argparse.Namespace) -> int:
    project = Project(Path(args.root))
    results = Path(args.results_dir)
    sessions = _sessions(results)
    env = os.environ
    now = datetime.now(UTC)
    started = min((datetime.fromisoformat(s["started_at"]) for s in sessions), default=now)
    finished = max((datetime.fromisoformat(s["finished_at"]) for s in sessions), default=now)
    repo = env.get("GITHUB_REPOSITORY")
    run_id = env.get("GITHUB_RUN_ID") or f"local-{now:%Y%m%dT%H%M%S}"
    run_url = (
        f"{env.get('GITHUB_SERVER_URL', 'https://github.com')}/{repo}/actions/runs/{run_id}"
        if repo and env.get("GITHUB_RUN_ID")
        else None
    )
    seeds = [s.get("random_seed") for s in sessions if s.get("random_seed") is not None]
    run = RunInfo(
        run_id=run_id,
        run_attempt=int(env.get("GITHUB_RUN_ATTEMPT", "1")),
        workflow=args.workflow,
        scope=args.scope,
        trigger=env.get("GITHUB_EVENT_NAME", "local"),
        commit_sha=env.get("GITHUB_SHA") or _git_sha(project.root),
        ref=env.get("GITHUB_REF"),
        repository=repo,
        run_url=run_url,
        started_at=started,
        finished_at=finished,
        random_seed=seeds[0] if seeds else None,
        reruns_configured=max((int(s.get("reruns", 0)) for s in sessions), default=0),
    )
    browser = next((s["browser"] for s in reversed(sessions) if s.get("browser")), None)
    first = sessions[0] if sessions else {}
    environment = Environment(
        kind="github-actions" if env.get("GITHUB_ACTIONS") == "true" else "local",
        os=env.get("ImageOS") or first.get("os") or f"{platform.system()} {platform.release()}",
        python=first.get("python", platform.python_version()),
        pytest=first.get("pytest"),
        selenium=_selenium_version(),
        browser=BrowserInfo(**browser) if browser else None,
        target_urls=[env.get("QA_BASE_URL", "https://wordcounter.net/")] if browser else [],
    )
    records = _read_jsonl(results / "attempts.jsonl")
    levels = frozenset(args.levels.split(",")) if args.levels else None
    result, issues = build_run_result(
        records, project.catalog(), run, environment, performance=_performance(results), levels=levels
    )
    gate = evaluate(result, load_policy(Path(args.policy)))
    result = result.model_copy(update={"gate": gate})
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(result.model_dump_json(indent=1), encoding="utf-8")
    for issue in issues:
        print(f"{issue.code}: {issue.message}", file=sys.stderr)
    s = result.summary
    print(
        f"{out}: {s.executed} ejecutados · {s.passed} PASS · {s.flaky} FLAKY · {s.failed} FAIL · "
        f"{s.blocked} BLOCKED · {s.skipped} SKIPPED · {s.not_run} NOT RUN · gate {gate.decision.value}"
    )
    return 1 if issues else 0


def _selenium_version() -> str | None:
    try:
        return version("selenium")
    except PackageNotFoundError:
        return None


def cmd_results_schema(_: argparse.Namespace) -> int:
    print(json.dumps(RunResult.model_json_schema(), indent=1, ensure_ascii=False))
    return 0


def _load_run(path: str) -> RunResult:
    return RunResult.model_validate_json(Path(path).read_text(encoding="utf-8"))


def cmd_report_summary(args: argparse.Namespace) -> int:
    run = _load_run(args.run)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    markdown = render_markdown(run)
    (out / "summary.md").write_text(markdown, encoding="utf-8")
    (out / "summary.html").write_text(render_html(run), encoding="utf-8")
    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if args.github_summary and step_summary:
        with open(step_summary, "a", encoding="utf-8") as handle:
            handle.write(markdown)
    print(markdown)
    return 0


def cmd_gate(args: argparse.Namespace) -> int:
    run = _load_run(args.run)
    policy = load_policy(Path(args.policy))
    result = evaluate(run, policy)
    print(f"Quality gate: {result.decision.value.upper()}")
    for reason in result.reasons:
        print(f"  - {reason}")
    return exit_code(result, policy)


def cmd_history_save(args: argparse.Namespace) -> int:
    run = _load_run(args.run)
    repo = FileSystemHistoryRepository(Path(args.history_dir))
    try:
        rel = repo.save_run(run)
    except DuplicateRunError as exc:
        print(f"corrida ya registrada, no se sobrescribe: {exc}")
        return 0
    print(rel)
    return 0


def cmd_portal_build(args: argparse.Namespace) -> int:
    project = Project(Path(args.root))
    runs = FileSystemHistoryRepository(Path(args.history_dir)).load_runs() if args.history_dir else []
    keys = {(r.run.workflow, r.key) for r in runs}
    for latest in args.latest or []:
        path = Path(latest)
        if path.exists():
            run = _load_run(latest)
            if (run.run.workflow, run.key) not in keys:
                runs.append(run)
    model = build_dashboard(runs, datetime.now(UTC))
    ctx = PortalContext(
        root=project.root,
        out_dir=Path(args.out).resolve(),
        repository=args.repository or os.environ.get("GITHUB_REPOSITORY"),
        code_ref=args.ref or os.environ.get("GITHUB_SHA") or _git_sha(project.root),
        requirements=project.requirements,
        cases=project.cases,
        bugs=project.bugs,
        implementations=project.implementations,
        model=model,
    )
    written = build_portal(ctx)
    print(f"{len(written)} páginas generadas en {ctx.out_dir} a partir de {len(runs)} corrida(s)")
    return 0


# --------------------------------------------------------------------------- parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qa", description="Farmatodo QA — herramientas de calidad")
    parser.add_argument("--root", default=".", help="raíz del repositorio")
    sub = parser.add_subparsers(dest="command", required=True)

    specs = sub.add_parser("specs").add_subparsers(dest="action", required=True)
    specs.add_parser("validate").set_defaults(func=cmd_specs_validate)
    gen = specs.add_parser("generate")
    gen.add_argument("--check", action="store_true")
    gen.set_defaults(func=cmd_specs_generate)

    results = sub.add_parser("results").add_subparsers(dest="action", required=True)
    build = results.add_parser("build")
    build.add_argument("--results-dir", default="reports")
    build.add_argument("--workflow", default="functional-tests")
    build.add_argument("--scope", choices=["functional", "performance"], default="functional")
    build.add_argument("--policy", default="config/quality-gate.yaml")
    build.add_argument(
        "--levels", default=None, help="niveles esperados en la corrida, p. ej. unit,integration,e2e"
    )
    build.add_argument("--out", default="reports/run-result.json")
    build.set_defaults(func=cmd_results_build)
    results.add_parser("schema").set_defaults(func=cmd_results_schema)

    report = sub.add_parser("report").add_subparsers(dest="action", required=True)
    summary = report.add_parser("summary")
    summary.add_argument("--run", default="reports/run-result.json")
    summary.add_argument("--out-dir", default="reports")
    summary.add_argument("--github-summary", action="store_true")
    summary.set_defaults(func=cmd_report_summary)

    gate = sub.add_parser("gate")
    gate.add_argument("--run", default="reports/run-result.json")
    gate.add_argument("--policy", default="config/quality-gate.yaml")
    gate.set_defaults(func=cmd_gate)

    history = sub.add_parser("history").add_subparsers(dest="action", required=True)
    save = history.add_parser("save")
    save.add_argument("--run", default="reports/run-result.json")
    save.add_argument("--history-dir", required=True)
    save.set_defaults(func=cmd_history_save)

    portal = sub.add_parser("portal").add_subparsers(dest="action", required=True)
    pbuild = portal.add_parser("build")
    pbuild.add_argument("--history-dir", default=None)
    pbuild.add_argument("--latest", action="append", help="run-result.json adicional (repetible)")
    pbuild.add_argument("--out", default="docs/generated")
    pbuild.add_argument("--repository", default=None, help="owner/repo para enlaces al código")
    pbuild.add_argument("--ref", default=None, help="commit o rama para enlaces al código")
    pbuild.set_defaults(func=cmd_portal_build)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
