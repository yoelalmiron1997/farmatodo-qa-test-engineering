"""Evaluación del gate: nunca convierte un fallo en PASS; a lo sumo lo baja a WARN de forma visible."""

from __future__ import annotations

from farmatodo_qa.quality_gate.policy import Action, GatePolicy
from farmatodo_qa.results.models import FinalStatus, GateDecision, GateResult, RunResult

_ORDER = {Action.PASS: 0, Action.WARN: 1, Action.INCONCLUSIVE: 2, Action.BLOCK: 3}


def evaluate(run: RunResult, policy: GatePolicy) -> GateResult:
    decision = Action.PASS
    reasons: list[str] = []
    for case in run.cases:
        gate_name, rule = policy.rule_for(case.priority)
        status = case.final_status
        if status is FinalStatus.FAIL:
            action = rule.on_fail
        elif status is FinalStatus.FLAKY:
            action = rule.on_flaky
        elif status is FinalStatus.BLOCKED:
            action = rule.on_blocked
        elif status is FinalStatus.NOT_RUN:
            action = rule.on_not_run
        else:
            continue
        label = f"{case.case_id} ({case.priority}) {status.value} → {action.value} [{gate_name}]"
        if status is FinalStatus.FAIL and case.known_defect:
            action = policy.known_defect_action
            label = f"{case.case_id} ({case.priority}) FAIL por defecto conocido {case.known_defect} → {action.value}"
        if case.case_id in policy.quarantine and action is Action.BLOCK:
            action = Action.WARN
            label += " (en cuarentena: se reporta, no bloquea)"
        if action is Action.PASS:
            continue
        reasons.append(label)
        if _ORDER[action] > _ORDER[decision]:
            decision = action
    return GateResult(decision=GateDecision(decision.value), reasons=reasons)


def exit_code(result: GateResult, policy: GatePolicy) -> int:
    if result.decision is GateDecision.BLOCK:
        return 1
    if result.decision is GateDecision.INCONCLUSIVE and policy.inconclusive_fails_job:
        return 1
    return 0
