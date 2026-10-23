"""Reporte resumen exigido por el PDF (REQ-RPT-001): ejecutados, aprobados, fallidos y el error.

Funciones puras ``RunResult → str`` (Markdown y HTML) para poder probarlas con datos sintéticos.
"""

from __future__ import annotations

import html
from collections import Counter
from dataclasses import dataclass

from farmatodo_qa.results.models import (
    EXECUTED_STATUSES,
    AttemptOutcome,
    CaseResult,
    FinalStatus,
    RunResult,
    TestExecution,
)

STATUS_LABEL = {
    FinalStatus.PASS: "PASS",
    FinalStatus.FLAKY: "FLAKY (falló y luego pasó)",
    FinalStatus.FAIL: "FAIL",
    FinalStatus.SKIPPED: "SKIPPED",
    FinalStatus.BLOCKED: "BLOCKED",
    FinalStatus.NOT_RUN: "NOT RUN",
}


@dataclass(frozen=True, slots=True)
class FailureRow:
    case: CaseResult
    execution: TestExecution
    category: str
    message: str
    evidence: tuple[str, ...]


def scenario_counts(run: RunResult) -> Counter[FinalStatus]:
    """Conteo por escenario (cada ejecución parametrizada es un escenario)."""
    return Counter(e.final_status for c in run.cases for e in c.executions)


def failure_rows(run: RunResult) -> list[FailureRow]:
    rows = []
    for case in run.cases:
        for execution in case.executions:
            if execution.final_status not in {FinalStatus.FAIL, FinalStatus.FLAKY}:
                continue
            failed = [a for a in execution.attempts if a.outcome is AttemptOutcome.FAILED]
            last = failed[-1] if failed else None
            rows.append(
                FailureRow(
                    case=case,
                    execution=execution,
                    category=str(last.category) if last and last.category else "unknown",
                    message=(last.message or last.exception_type or "sin mensaje") if last else "sin mensaje",
                    evidence=tuple(e for a in failed for e in a.evidence),
                )
            )
    return rows


def _pct(value: float | None) -> str:
    return "—" if value is None else f"{value:.1%}"


def _one_line(text: str, limit: int = 400) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= limit else flat[: limit - 1] + "…"


def render_markdown(run: RunResult) -> str:
    s = run.summary
    sc = scenario_counts(run)
    executed_scenarios = sum(sc[st] for st in EXECUTED_STATUSES)
    gate = run.gate.decision.value.upper() if run.gate else "NO EVALUADO"
    lines = [
        f"# Reporte resumen — {run.run.workflow} #{run.run.run_id}",
        "",
        f"- **Fecha:** {run.run.started_at:%Y-%m-%d %H:%M} UTC · **Commit:** `{run.run.commit_sha[:12]}`"
        f" · **Entorno:** {run.environment.kind} / {run.environment.os}"
        + (
            f" · **Navegador:** {run.environment.browser.name} {run.environment.browser.version or ''}"
            if run.environment.browser
            else ""
        ),
        f"- **Quality gate:** {gate}" + (f" · [workflow]({run.run.run_url})" if run.run.run_url else ""),
        "",
        "## Totales",
        "",
        "| Unidad | Ejecutados | Aprobados | Flaky | Fallidos | Omitidos | Bloqueados | No ejecutados |",
        "|---|---|---|---|---|---|---|---|",
        f"| Escenarios (tests) | {executed_scenarios} | {sc[FinalStatus.PASS]} | {sc[FinalStatus.FLAKY]} | "
        f"{sc[FinalStatus.FAIL]} | {sc[FinalStatus.SKIPPED]} | {sc[FinalStatus.BLOCKED]} | — |",
        f"| Casos especificados | {s.executed} | {s.passed} | {s.flaky} | {s.failed} | {s.skipped} | "
        f"{s.blocked} | {s.not_run} |",
        "",
        f"Intentos: {s.attempts} · reintentos: {s.retries} · aprobación al primer intento: "
        f"{_pct(s.first_attempt_pass_rate)} · aprobación final: {_pct(s.final_pass_rate)} · "
        f"flaky observado: {_pct(s.flaky_rate)} · duración: {s.duration_s:.1f} s",
        "",
        "> *Aprobados* cuenta solo PASS limpios (primer intento). Un FLAKY nunca se suma a los aprobados.",
        "",
    ]
    rows = failure_rows(run)
    lines += ["## Fallos y descripción del error", ""]
    if rows:
        lines += [
            "| Caso | Prioridad | Escenario | Estado | Categoría | Descripción del error | Evidencia |",
            "|---|---|---|---|---|---|---|",
        ]
        for row in rows:
            known = f" · defecto conocido {row.case.known_defect}" if row.case.known_defect else ""
            lines.append(
                f"| {row.case.case_id} — {row.case.title} | {row.case.priority} | `{row.execution.param_id or '-'}` | "
                f"{STATUS_LABEL[row.execution.final_status]}{known} | {row.category} | "
                f"{_one_line(row.message).replace('|', '\\|')} | {', '.join(row.evidence) or '—'} |"
            )
    else:
        lines.append("Sin fallos en esta corrida.")
    blocked = [(c, e) for c in run.cases for e in c.executions if e.final_status is FinalStatus.BLOCKED]
    if blocked:
        lines += ["", "## Bloqueados (dependencia externa)", ""]
        lines += [
            f"- {c.case_id} `{e.param_id or '-'}`: {e.blocked_reason or 'sin motivo'}" for c, e in blocked
        ]
    not_run = [c for c in run.cases if c.final_status is FinalStatus.NOT_RUN]
    if not_run:
        lines += ["", "## No ejecutados", ""]
        lines += [f"- {c.case_id} — {c.title} ({c.priority})" for c in not_run]
    if run.gate and run.gate.reasons:
        lines += ["", "## Motivos del quality gate", ""] + [f"- {r}" for r in run.gate.reasons]
    return "\n".join(lines) + "\n"


def render_html(run: RunResult) -> str:
    s = run.summary
    sc = scenario_counts(run)
    esc = html.escape
    rows = (
        "".join(
            f"<tr><td>{esc(r.case.case_id)}</td><td>{esc(r.case.title)}</td><td>{r.case.priority}</td>"
            f"<td><code>{esc(r.execution.param_id or '-')}</code></td><td>{esc(STATUS_LABEL[r.execution.final_status])}</td>"
            f"<td>{esc(r.category)}</td><td><pre>{esc(_one_line(r.message, 1200))}</pre></td>"
            f"<td>{esc(', '.join(r.evidence) or '—')}</td></tr>"
            for r in failure_rows(run)
        )
        or '<tr><td colspan="8">Sin fallos en esta corrida.</td></tr>'
    )
    executed_scenarios = sum(sc[st] for st in EXECUTED_STATUSES)
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Reporte resumen {esc(run.run.run_id)}</title>
<style>body{{font-family:system-ui,sans-serif;margin:1.5rem;color:#1b1b1b}}table{{border-collapse:collapse;width:100%}}
td,th{{border:1px solid #ccc;padding:.4rem;text-align:left;vertical-align:top}}th{{background:#f2f4f7}}
pre{{white-space:pre-wrap;margin:0;font-size:.85rem}}.k{{display:inline-block;margin-right:1.5rem}}</style></head>
<body><h1>Reporte resumen — {esc(run.run.workflow)} #{esc(run.run.run_id)}</h1>
<p>{run.run.started_at:%Y-%m-%d %H:%M} UTC · commit <code>{esc(run.run.commit_sha[:12])}</code> ·
quality gate: <strong>{esc(run.gate.decision.value.upper() if run.gate else "NO EVALUADO")}</strong></p>
<p><span class="k">Escenarios ejecutados: <strong>{executed_scenarios}</strong></span>
<span class="k">Aprobados: <strong>{sc[FinalStatus.PASS]}</strong></span>
<span class="k">Flaky: <strong>{sc[FinalStatus.FLAKY]}</strong></span>
<span class="k">Fallidos: <strong>{sc[FinalStatus.FAIL]}</strong></span>
<span class="k">Omitidos: {sc[FinalStatus.SKIPPED]}</span><span class="k">Bloqueados: {sc[FinalStatus.BLOCKED]}</span></p>
<p>Casos: {s.executed} ejecutados de {s.specified} especificados · intentos {s.attempts} · reintentos {s.retries}</p>
<h2>Fallos y descripción del error</h2>
<table><thead><tr><th>Caso</th><th>Título</th><th>Prioridad</th><th>Escenario</th><th>Estado</th><th>Categoría</th>
<th>Descripción del error</th><th>Evidencia</th></tr></thead><tbody>{rows}</tbody></table></body></html>
"""
