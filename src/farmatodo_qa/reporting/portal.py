"""Generación de las páginas del portal (adaptador: escribe en ``docs/generated``).

Todo número publicado indica su procedencia (corrida, fecha, commit). Sin corridas, las
páginas lo dicen explícitamente.
"""

from __future__ import annotations

import json
import re
import shutil
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from farmatodo_qa.reporting.dashboard_model import DashboardModel
from farmatodo_qa.reporting.summary import STATUS_LABEL, failure_rows
from farmatodo_qa.results.models import FinalStatus, RunResult
from farmatodo_qa.specs.models import BugReport, CaseSpec, ImplementationRef, Requirement
from farmatodo_qa.traceability.catalog import (
    automation_coverage,
    automation_label,
    cases_for,
    catalog_summary,
    render_inventory,
    specification_coverage,
)

NO_DATA = (
    '!!! info "Sin ejecuciones registradas todavía"\n'
    "    Esta sección se completa automáticamente cuando GitHub Actions publica la primera corrida "
    "en la rama `qa-history`. No se muestran valores inventados.\n"
)


@dataclass(frozen=True, slots=True)
class PortalContext:
    root: Path
    out_dir: Path
    repository: str | None  # owner/repo
    code_ref: str  # commit SHA o rama para los enlaces al código
    requirements: Sequence[Requirement]
    cases: Sequence[CaseSpec]
    bugs: Sequence[BugReport]
    implementations: Sequence[ImplementationRef]
    model: DashboardModel

    def code_url(self, path: str, line: int | None = None) -> str | None:
        if not self.repository:
            return None
        anchor = f"#L{line}" if line else ""
        return f"https://github.com/{self.repository}/blob/{self.code_ref}/{path}{anchor}"


def badge(status: FinalStatus | str) -> str:
    value = status.value if isinstance(status, FinalStatus) else str(status)
    css = re.sub(r"[^a-z0-9-]", "", value.lower().replace("_", "-"))
    return f'<span class="qa-badge qa-{css}">{value.replace("_", " ")}</span>'


def _pct(value: float | None) -> str:
    return "—" if value is None else f"{value:.1%}"


def _fmt_dt(value: datetime) -> str:
    return f"{value:%Y-%m-%d %H:%M} UTC"


def _run_ref(run: RunResult) -> str:
    link = f"[{run.run.workflow} #{run.run.run_id}]({run.run.run_url})" if run.run.run_url else run.key
    return f"{link} · {_fmt_dt(run.run.started_at)} · commit `{run.run.commit_sha[:10]}`"


def _latest_status(ctx: PortalContext) -> dict[str, FinalStatus]:
    statuses: dict[str, FinalStatus] = {}
    for run in (ctx.model.latest_functional, ctx.model.latest_performance):
        if run:
            statuses.update({c.case_id: c.final_status for c in run.cases})
    return statuses


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# --------------------------------------------------------------------------- páginas


def render_dashboard(ctx: PortalContext) -> str:
    """Se incluye en ``docs/index.md``: los enlaces son relativos a la raíz de ``docs``."""
    m = ctx.model
    impl = {r.case_id for r in ctx.implementations}
    lines = [
        "<!-- Generado por `qa portal build`; no editar a mano. -->",
        f"_Portal generado el {_fmt_dt(m.generated_at)}_"
        + (f" · [Repositorio](https://github.com/{ctx.repository})" if ctx.repository else ""),
        "",
        "## Estado de la última ejecución funcional",
        "",
    ]
    run = m.latest_functional
    if run is None:
        lines.append(NO_DATA)
    else:
        s = run.summary
        gate = run.gate.decision.value if run.gate else "n/a"
        lines += [
            f"**Quality gate:** {badge(gate.upper())} · {_run_ref(run)}",
            "",
            '<div class="qa-kpis" markdown>',
            "",
            "| Ejecutados | PASS limpio | FLAKY | FAIL | SKIPPED | BLOCKED | NOT RUN | Reintentos |",
            "|---|---|---|---|---|---|---|---|",
            f"| {s.executed} | {s.passed} | {s.flaky} | {s.failed} | {s.skipped} | {s.blocked} | "
            f"{s.not_run} | {s.retries} |",
            "",
            "</div>",
            "",
            f"Aprobación al primer intento **{_pct(s.first_attempt_pass_rate)}** · aprobación final "
            f"{_pct(s.final_pass_rate)} · flaky observado {_pct(s.flaky_rate)} · duración "
            f"{s.duration_s:.0f} s · tiempo medio por caso "
            f"{'—' if s.mean_case_duration_s is None else f'{s.mean_case_duration_s:.1f} s'}",
            "",
        ]
        if run.gate and run.gate.reasons:
            lines += (
                ['??? warning "Motivos del quality gate"', ""]
                + [f"    - {r}" for r in run.gate.reasons]
                + [""]
            )
    lines += ["## Cobertura", "", "| Indicador | Valor | Definición |", "|---|---|---|"]
    for cov in specification_coverage(ctx.requirements, ctx.cases):
        lines.append(
            f"| {cov.label} | {cov.numerator}/{cov.denominator} ({_pct(cov.ratio)}) | "
            "requisitos con ≥ 1 caso o verificación no-test declarada |"
        )
    for cov in automation_coverage(ctx.cases, impl):
        lines.append(
            f"| {cov.label} | {cov.numerator}/{cov.denominator} ({_pct(cov.ratio)}) | "
            "casos automatizables con test vinculado por marker |"
        )
    if run is not None:
        executed_reqs = {
            rid
            for c in ctx.cases
            for rid in c.meta.requirement_ids
            if any(
                rc.case_id == c.id
                and rc.final_status in {FinalStatus.PASS, FinalStatus.FLAKY, FinalStatus.FAIL}
                for rc in run.cases
            )
        }
        test_reqs = [r for r in ctx.requirements if r.verification == "test"]
        done = sum(1 for r in test_reqs if r.id in executed_reqs)
        lines.append(
            f"| Requisitos ejecutados (última corrida) | {done}/{len(test_reqs)} "
            f"({_pct(done / len(test_reqs) if test_reqs else None)}) | requisitos `test` con ≥ 1 caso ejecutado |"
        )
    lines += [
        "",
        "> La cobertura de requisitos **no** es cobertura de código ni tasa de aprobación: son tres "
        "indicadores distintos ([definiciones](strategy/metrics.md)).",
        "",
        "## Catálogo",
        "",
        catalog_summary(ctx.cases, ctx.requirements),
        "",
        "## Tendencia",
        "",
    ]
    if m.trend:
        lines += [
            '<canvas class="qa-chart" data-chart="trend" data-src="generated/data/trend.json" height="110"></canvas>',
            "",
            "| Corrida | Fecha | Commit | Ejecutados | PASS | FLAKY | FAIL | BLOCKED | Gate |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for p in reversed(m.trend[-15:]):
            ref = f"[{p.run_key}]({p.run_url})" if p.run_url else p.run_key
            lines.append(
                f"| {ref} | {_fmt_dt(p.started_at)} | `{p.commit_sha[:8]}` | {p.executed} | {p.passed} | "
                f"{p.flaky} | {p.failed} | {p.blocked} | {badge(p.gate.upper())} |"
            )
    else:
        lines.append(NO_DATA)
    lines += ["", "## Performance (P2)", ""]
    if m.performance:
        lines += ["| Escenario | Serie | n | Mediana (ms) | Estado vs baseline |", "|---|---|---|---|---|"]
        for v in m.performance:
            med = "—" if v.latest.median is None else f"{v.latest.median:.0f}"
            lines.append(f"| {v.case_id} | {v.series} | {v.latest.n} | {med} | {v.comparison.status.value} |")
        lines.append("\nDetalle en [Performance](generated/performance.md).")
    else:
        lines.append(NO_DATA)
    return "\n".join(lines) + "\n"


def render_test_cases(ctx: PortalContext) -> str:
    impl = {r.case_id for r in ctx.implementations}
    status = _latest_status(ctx)
    lines = [
        "# Casos de prueba",
        "",
        catalog_summary(ctx.cases, ctx.requirements),
        "",
        '<input class="qa-filter" type="search" placeholder="Filtrar por ID, requisito, tipo, nivel o resultado…" '
        'aria-label="Filtrar casos">',
        "",
    ]
    for priority in ("P0", "P1", "P2"):
        group = [c for c in ctx.cases if c.meta.priority == priority]
        lines += [
            f"## {priority} ({len(group)})",
            "",
            "| ID | Título | Requisitos | Tipo | Nivel | Automatización | Último resultado |",
            "|---|---|---|---|---|---|---|",
        ]
        for c in group:
            st = status.get(c.id)
            shown = badge(st) if st else ("manual" if c.meta.automation == "manual" else badge("NOT_RUN"))
            lines.append(
                f"| [{c.id}](cases/{c.id}.md) | {c.meta.title} | {', '.join(c.meta.requirement_ids)} | "
                f"{c.meta.test_type} | {c.meta.level} | {automation_label(c, impl)} | {shown} |"
            )
        lines.append("")
    lines += ["## Inventario con riesgo y justificación", "", render_inventory(ctx.cases, impl), ""]
    return "\n".join(lines)


def render_requirements(ctx: PortalContext) -> str:
    lines = ["# Requisitos", "", "Fuente: `specs/requirements/requirements.yaml`.", ""]
    for req in ctx.requirements:
        related = cases_for(req.id, ctx.cases)
        lines += [
            f"## {req.id}",
            "",
            f"**{req.statement}**",
            "",
            f"Fuente: {req.source} · Ejercicio: {req.exercise} · Verificación: `{req.verification}`",
            "",
            "Criterios de aceptación:",
            "",
            *[f"- {ac}" for ac in req.acceptance_criteria],
            "",
            "Casos: " + (", ".join(f"[{c.id}](cases/{c.id}.md) ({c.meta.priority})" for c in related) or "—"),
            "",
        ]
    return "\n".join(lines)


def render_traceability_page(ctx: PortalContext) -> str:
    status = _latest_status(ctx)
    impl_by_case: dict[str, list[ImplementationRef]] = {}
    for ref in ctx.implementations:
        impl_by_case.setdefault(ref.case_id, []).append(ref)
    bugs_by_case: dict[str, list[BugReport]] = {}
    for bug in ctx.bugs:
        for cid in bug.related_cases:
            bugs_by_case.setdefault(cid, []).append(bug)
    run = ctx.model.latest_functional
    lines = [
        "# Matriz de trazabilidad",
        "",
        "Requisito → Riesgo → Caso → Prioridad → Implementación → Ejecución → Resultado → Evidencia → Defecto.",
        "",
        f"Última corrida funcional: {_run_ref(run)}" if run else NO_DATA,
        "",
        "| Requisito | Caso | Riesgo | Prioridad | Implementación | Resultado | Evidencia | Defecto |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for req in ctx.requirements:
        related = cases_for(req.id, ctx.cases)
        if not related:
            lines.append(f"| {req.id} | — (verificación por {req.verification}) | — | — | — | — | — | — |")
        for case in related:
            refs = impl_by_case.get(case.id, [])
            impl = "<br>".join(
                f"[{Path(r.path).name}:{r.line}]({ctx.code_url(r.path, r.line)})"
                if ctx.code_url(r.path)
                else f"`{r.path}:{r.line}`"
                for r in refs[:3]
            ) or ("manual" if case.meta.automation == "manual" else "—")
            st = status.get(case.id)
            evidence = "—"
            if run and st in {FinalStatus.FAIL, FinalStatus.FLAKY} and run.run.run_url:
                evidence = f"[artifacts]({run.run.run_url})"
            defects = (
                ", ".join(f"[{b.id}](../bugs/{Path(b.path).stem}.md)" for b in bugs_by_case.get(case.id, []))
                or "—"
            )
            lines.append(
                f"| {req.id} | [{case.id}](cases/{case.id}.md) | {case.meta.risk} | {case.meta.priority} | "
                f"{impl} | {badge(st) if st else '—'} | {evidence} | {defects} |"
            )
    return "\n".join(lines) + "\n"


def render_case_page(ctx: PortalContext, case: CaseSpec) -> str:
    meta = case.meta
    reqs = {r.id: r for r in ctx.requirements}
    refs = [r for r in ctx.implementations if r.case_id == case.id]
    history = ctx.model.case_history.get(case.id, ())
    bugs = [b for b in ctx.bugs if case.id in b.related_cases or b.id == meta.known_defect]
    body = re.sub(r"\n## Implementación\n.*", "", case.body, flags=re.S).strip()
    body = re.sub(r"^# .*\n", "", body).strip()
    lines = [
        f"# {meta.id} — {meta.title}",
        "",
        f"{badge(history[0].status) if history else badge('NOT_RUN')} · **{meta.priority}** · riesgo {meta.risk} "
        f"({meta.risk_assessment.impact}×{meta.risk_assessment.likelihood}={meta.risk_assessment.score}) · "
        f"{meta.test_type} · {meta.level} · automatización: {meta.automation}",
        "",
        "## Requisitos asociados",
        "",
    ]
    for rid in meta.requirement_ids:
        req = reqs.get(rid)
        lines.append(f"- **{rid}** — {req.statement if req else 'inexistente'} ({req.source if req else ''})")
    lines += ["", body, "", "## Implementación", ""]
    if refs:
        for r in refs:
            url = ctx.code_url(r.path, r.line)
            lines.append(f"- [`{r.path}::{r.test_name}`]({url})" if url else f"- `{r.path}::{r.test_name}`")
    else:
        lines.append("- Caso manual: ver los reportes enlazados." if meta.automation == "manual" else "- —")
    lines += ["", "## Historial de ejecución", ""]
    if history:
        lines += [
            "| Corrida | Fecha | Commit | Resultado | Intentos | Detalle |",
            "|---|---|---|---|---|---|",
        ]
        for h in history[:20]:
            ref = f"[{h.run_key}]({h.run_url})" if h.run_url else h.run_key
            detail = "<br>".join(m.replace("|", "\\|")[:160] for m in h.messages[:2]) or "—"
            lines.append(
                f"| {ref} | {_fmt_dt(h.started_at)} | `{h.commit_sha[:8]}` | {badge(h.status)} | {h.attempts} | {detail} |"
            )
    else:
        lines.append(NO_DATA if meta.automation != "manual" else "Caso manual, sin ejecución automatizada.")
    stab = ctx.model.stability.get(case.id)
    if stab:
        lines += [
            "",
            f"Estabilidad (ventana comparable, n = {stab.n}): {_pct(stab.stability)} · flip rate "
            f"{_pct(stab.flip_rate)} · flaky observados {stab.flaky_observed}"
            + (" · **flaky sospechado**" if stab.suspected else ""),
        ]
    lines += ["", "## Defectos relacionados", ""]
    lines += [f"- [{b.id}](../../bugs/{Path(b.path).stem}.md) — {b.title}" for b in bugs] or ["- —"]
    lines += ["", f"<small>Fuente: `{case.path}` · {case.spec_hash}</small>", ""]
    return "\n".join(lines)


def render_execution(ctx: PortalContext) -> str:
    run = ctx.model.latest_functional
    lines = ["# Ejecución de pruebas", ""]
    if run is None:
        return "\n".join([*lines, NO_DATA])
    s = run.summary
    lines += [
        f"Última corrida: {_run_ref(run)}",
        "",
        f"Entorno: {run.environment.kind} · {run.environment.os} · Python {run.environment.python}"
        + (f" · pytest {run.environment.pytest}" if run.environment.pytest else "")
        + (f" · Selenium {run.environment.selenium}" if run.environment.selenium else "")
        + (
            f" · {run.environment.browser.name} {run.environment.browser.version or ''}"
            if run.environment.browser
            else ""
        ),
        "",
        f"Duración total {s.duration_s:.0f} s · intentos {s.attempts} · reintentos {s.retries} "
        f"(reintentos configurados: {run.run.reruns_configured})",
        "",
        "## Fallos y flaky",
        "",
    ]
    rows = failure_rows(run)
    if rows:
        lines += [
            "| Caso | Escenario | Estado | Categoría | Excepción / mensaje | Evidencia |",
            "|---|---|---|---|---|---|",
        ]
        for r in rows:
            msg = " ".join(r.message.split())[:300].replace("|", "\\|")
            ev = (
                f"[artifacts]({run.run.run_url})"
                if r.evidence and run.run.run_url
                else ", ".join(r.evidence) or "—"
            )
            lines.append(
                f"| [{r.case.case_id}](cases/{r.case.case_id}.md) | `{r.execution.param_id or '-'}` | "
                f"{STATUS_LABEL[r.execution.final_status]} | {r.category} | {msg} | {ev} |"
            )
        lines += [
            "",
            "> Capturas y DOM de cada intento fallido se adjuntan como artifacts de la corrida "
            "(retención configurada en el workflow).",
        ]
    else:
        lines.append("Sin fallos en la última corrida.")
    lines += [
        "",
        "## Todos los escenarios",
        "",
        "| Caso | Escenario | Estado | Intentos | Duración (s) |",
        "|---|---|---|---|---|",
    ]
    for case in run.cases:
        for e in case.executions:
            dur = sum(a.duration_s for a in e.attempts)
            lines.append(
                f"| [{case.case_id}](cases/{case.case_id}.md) | `{e.param_id or '-'}` | {badge(e.final_status)} | "
                f"{len(e.attempts)} | {dur:.2f} |"
            )
        if not case.executions:
            lines.append(
                f"| [{case.case_id}](cases/{case.case_id}.md) | — | {badge(case.final_status)} | 0 | — |"
            )
    lines += ["", "## Historial", ""]
    lines += [
        "| Corrida | Fecha | Ejecutados | PASS | FLAKY | FAIL | BLOCKED | Gate |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for p in reversed(ctx.model.trend[-30:]):
        ref = f"[{p.run_key}]({p.run_url})" if p.run_url else p.run_key
        lines.append(
            f"| {ref} | {_fmt_dt(p.started_at)} | {p.executed} | {p.passed} | {p.flaky} | {p.failed} | "
            f"{p.blocked} | {badge(p.gate.upper())} |"
        )
    return "\n".join(lines) + "\n"


def render_flaky(ctx: PortalContext) -> str:
    m = ctx.model
    lines = [
        "# Flaky tests",
        "",
        '!!! note "Observado vs sospechado"',
        "    **FLAKY observado**: en una misma corrida el test falló y luego pasó en un reintento. "
        "**Flaky sospechado**: en corridas comparables (mismo caso, misma especificación, mismo entorno) el "
        "resultado alterna entre PASS y FAIL; requiere investigación. Un FLAKY nunca se cuenta como PASS limpio.",
        "",
    ]
    run = m.latest_functional
    if run is None:
        return "\n".join([*lines, NO_DATA])
    s = run.summary
    suspected = [st for st in m.stability.values() if st.suspected]
    lines += [
        f"Última corrida: {_run_ref(run)}",
        "",
        "| Indicador | Valor | Fórmula |",
        "|---|---|---|",
        f"| Casos ejecutados | {s.executed} | casos con estado PASS, FLAKY o FAIL |",
        f"| Casos con reintentos | {s.cases_with_retries} | casos con alguna ejecución de más de 1 intento |",
        f"| Reintentos totales | {s.retries} | Σ (intentos − 1) por ejecución |",
        f"| FLAKY observados | {s.flaky} | último intento PASS tras ≥ 1 fallo |",
        f"| FAIL final | {s.failed} | último intento fallido |",
        f"| % flaky observado | {_pct(s.flaky_rate)} | FLAKY / ejecutados |",
        f"| Flaky sospechados (histórico) | {len(suspected)} | ver regla en el SDD, Anexo C.3 |",
        "",
        "## Distribución por prioridad (última corrida)",
        "",
        "| P0 | P1 | P2 |",
        "|---|---|---|",
        f"| {m.flaky_by_priority.get('P0', 0)} | {m.flaky_by_priority.get('P1', 0)} | {m.flaky_by_priority.get('P2', 0)} |",
        "",
        "## Fallos por categoría (intentos)",
        "",
    ]
    if s.failures_by_category:
        lines += ["| Categoría | Intentos fallidos |", "|---|---|"]
        lines += [f"| {k} | {v} |" for k, v in s.failures_by_category.items()]
        lines.append("\n> Las categorías son observaciones técnicas, no diagnósticos definitivos.")
    else:
        lines.append("Sin intentos fallidos en la última corrida.")
    lines += ["", "## Top 10 más inestables", ""]
    if m.top_unstable:
        lines += [
            "| Caso | Prioridad | n | Estabilidad | Flip rate | FLAKY | FAIL | Sospechado |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for st in m.top_unstable:
            lines.append(
                f"| [{st.case_id}](cases/{st.case_id}.md) | {st.priority} | {st.n} | {_pct(st.stability)} | "
                f"{_pct(st.flip_rate)} | {st.flaky_observed} | {st.failures} | {'sí' if st.suspected else 'no'} |"
            )
    else:
        lines.append("Ningún caso con menos de 100 % de estabilidad en la ventana comparable (n ≥ 3).")
    lines += [
        "",
        "## Evolución",
        "",
        "| Corrida | Fecha | FLAKY | Reintentos | FAIL |",
        "|---|---|---|---|---|",
    ]
    for p in reversed(m.trend[-30:]):
        lines.append(f"| {p.run_key} | {_fmt_dt(p.started_at)} | {p.flaky} | {p.retries} | {p.failed} |")
    return "\n".join(lines) + "\n"


def render_performance(ctx: PortalContext) -> str:
    m = ctx.model
    lines = [
        "# Performance (P2)",
        "",
        '!!! warning "Limitaciones"',
        "    Mediciones ligeras, secuenciales y sin concurrencia contra un sitio de terceros, desde runners "
        "compartidos de GitHub. Son descriptivas: el estado *alert* es un cambio significativo según una regla "
        "documentada, no una prueba estadística de regresión. Con menos de 20 muestras no se publica P95. "
        "*end_to_end* incluye la latencia de WebDriver y la resolución del sondeo; *in_browser* se mide con "
        "`MutationObserver` + `performance.now()` dentro de la página.",
        "",
    ]
    if not m.performance:
        return "\n".join([*lines, NO_DATA])
    run = m.latest_performance
    if run:
        lines += [f"Última medición: {_run_ref(run)}", ""]
    lines += [
        '<canvas class="qa-chart" data-chart="perf" data-src="data/performance.json" height="120"></canvas>',
        "",
        "| Escenario | Serie | n | Mín | Media | Mediana | Máx | Desvío | P95 | Baseline | Estado | Entorno |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]

    def f(v: float | None) -> str:
        return "—" if v is None else f"{v:.0f}"

    for v in m.performance:
        st = v.latest
        lines.append(
            f"| {v.case_id} | {v.series} | {st.n} | {f(st.minimum)} | {f(st.mean)} | {f(st.median)} | "
            f"{f(st.maximum)} | {f(st.stdev)} | {f(st.p95)} | {f(v.comparison.baseline_ms)} | "
            f"{v.comparison.status.value} | {v.environment} |"
        )
    warnings = sorted({w for v in m.performance for w in v.latest.warnings})
    if warnings:
        lines += ["", *[f"- {w}" for w in warnings]]
    lines += ["", "Valores en milisegundos."]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- datos y build


def chart_data(model: DashboardModel) -> Mapping[str, object]:
    return {
        "trend": {
            "labels": [f"{p.started_at:%m-%d %H:%M}" for p in model.trend[-30:]],
            "series": {
                "PASS": [p.passed for p in model.trend[-30:]],
                "FLAKY": [p.flaky for p in model.trend[-30:]],
                "FAIL": [p.failed for p in model.trend[-30:]],
                "BLOCKED": [p.blocked for p in model.trend[-30:]],
            },
        },
        "performance": {
            "series": [
                {
                    "label": f"{v.case_id} · {v.series}",
                    "points": [{"x": f"{d:%Y-%m-%d %H:%M}", "y": round(val, 1)} for d, val in v.history],
                }
                for v in model.performance
            ]
        },
    }


def build_portal(ctx: PortalContext) -> list[Path]:
    out = ctx.out_dir
    if out.exists():
        shutil.rmtree(out)
    pages: dict[str, str] = {
        "dashboard.md": render_dashboard(ctx),
        "test-cases.md": render_test_cases(ctx),
        "requirements.md": render_requirements(ctx),
        "traceability.md": render_traceability_page(ctx),
        "execution.md": render_execution(ctx),
        "flaky.md": render_flaky(ctx),
        "performance.md": render_performance(ctx),
    }
    for case in ctx.cases:
        pages[f"cases/{case.id}.md"] = render_case_page(ctx, case)
    sdd = ctx.root / "specs" / "SDD.md"
    if sdd.exists():
        # sdd.md y cases/ quedan en el mismo directorio: los enlaces relativos del SDD siguen funcionando.
        pages["sdd.md"] = sdd.read_text(encoding="utf-8")
    for adr in sorted((ctx.root / "specs" / "decisions").glob("ADR-*.md")):
        pages[f"decisions/{adr.name}"] = adr.read_text(encoding="utf-8")
    written = []
    for rel, content in pages.items():
        _write(out / rel, content)
        written.append(out / rel)
    data = chart_data(ctx.model)
    for name, payload in data.items():
        _write(out / "data" / f"{name}.json", json.dumps(payload, ensure_ascii=False))
    return written
