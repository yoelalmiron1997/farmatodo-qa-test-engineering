"""Quality gate (TC-FW-008): nunca convierte un fallo en verde."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from farmatodo_qa.quality_gate import Action, GatePolicy, default_policy, evaluate, exit_code
from farmatodo_qa.results.models import GateDecision
from support.factories import O, case, run

ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.case("TC-FW-008")
@pytest.mark.parametrize(
    ("priority", "outcomes", "decision", "code"),
    [
        ("P0", (O.FAILED, O.FAILED, O.FAILED), GateDecision.BLOCK, 1),
        ("P0", (O.FAILED, O.PASSED), GateDecision.BLOCK, 1),
        ("P0", (O.BLOCKED,), GateDecision.INCONCLUSIVE, 1),
        ("P0", (), GateDecision.INCONCLUSIVE, 1),
        ("P1", (O.FAILED,), GateDecision.BLOCK, 1),
        ("P1", (O.FAILED, O.PASSED), GateDecision.WARN, 0),
        ("P2", (O.FAILED,), GateDecision.WARN, 0),
        ("P2", (O.FAILED, O.PASSED), GateDecision.WARN, 0),
        ("P0", (O.PASSED,), GateDecision.PASS, 0),
    ],
    ids=[
        "p0-fail",
        "p0-flaky",
        "p0-blocked",
        "p0-not-run",
        "p1-fail",
        "p1-flaky",
        "p2-fail",
        "p2-flaky",
        "todo-pass",
    ],
)
def test_default_policy(priority: str, outcomes: tuple[O, ...], decision: GateDecision, code: int) -> None:
    c = case("TC-WC-001", outcomes, priority=priority) if outcomes else case("TC-WC-001", priority=priority)
    result = evaluate(run([c]), default_policy())
    assert result.decision is decision
    assert exit_code(result, default_policy()) == code
    if decision is not GateDecision.PASS:
        assert result.reasons
        assert "TC-WC-001" in result.reasons[0]


@pytest.mark.case("TC-FW-008")
def test_alternative_policy_can_downgrade_p0_flaky_to_warning() -> None:
    policy = default_policy()
    gates = dict(policy.gates)
    gates["critical"] = gates["critical"].model_copy(update={"on_flaky": Action.WARN})
    relaxed = policy.model_copy(update={"gates": gates})
    result = evaluate(run([case("TC-WC-001", (O.FAILED, O.PASSED))]), relaxed)
    assert result.decision is GateDecision.WARN


@pytest.mark.case("TC-FW-008")
def test_known_defect_failure_is_visible_warning() -> None:
    c = case("TC-WC-017", (O.FAILED, O.FAILED, O.FAILED), priority="P2", known_defect="BUG-WC-001")
    result = evaluate(run([c]), default_policy())
    assert result.decision is GateDecision.WARN
    assert "BUG-WC-001" in result.reasons[0]


@pytest.mark.case("TC-FW-008")
def test_quarantine_downgrades_but_keeps_failure_visible() -> None:
    policy = default_policy().model_copy(update={"quarantine": ["TC-WC-001"]})
    result = evaluate(run([case("TC-WC-001", (O.FAILED,))]), policy)
    assert result.decision is GateDecision.WARN
    assert "cuarentena" in result.reasons[0]


@pytest.mark.case("TC-FW-008")
def test_versioned_policy_file_matches_documented_defaults() -> None:
    data = yaml.safe_load((ROOT / "config/quality-gate.yaml").read_text(encoding="utf-8"))
    assert GatePolicy.from_mapping(data) == default_policy()
