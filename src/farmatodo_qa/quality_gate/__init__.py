"""Quality gate configurable (SDD Anexo C.5)."""

from farmatodo_qa.quality_gate.evaluator import evaluate, exit_code
from farmatodo_qa.quality_gate.policy import Action, GatePolicy, GateRule, default_policy

__all__ = ["Action", "GatePolicy", "GateRule", "default_policy", "evaluate", "exit_code"]
