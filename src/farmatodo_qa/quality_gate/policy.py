"""Política del quality gate como datos (``config/quality-gate.yaml``)."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Action(StrEnum):
    PASS = "pass"
    WARN = "warn"
    INCONCLUSIVE = "inconclusive"
    BLOCK = "block"


class GateRule(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    priorities: list[Literal["P0", "P1", "P2"]] = Field(min_length=1)
    on_fail: Action
    on_flaky: Action
    on_blocked: Action
    on_not_run: Action = Action.WARN


class GatePolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[1] = 1
    gates: dict[str, GateRule]
    known_defect_action: Action = Action.WARN
    inconclusive_fails_job: bool = True
    # Lista explícita y visible: el caso se ejecuta y se reporta; solo baja block → warn.
    quarantine: list[str] = Field(default_factory=list)

    def rule_for(self, priority: str) -> tuple[str, GateRule]:
        for name, rule in self.gates.items():
            if priority in rule.priorities:
                return name, rule
        raise KeyError(f"ninguna regla del gate cubre la prioridad {priority}")

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> GatePolicy:
        return cls.model_validate(data)


def default_policy() -> GatePolicy:
    return GatePolicy(
        gates={
            "critical": GateRule(
                priorities=["P0"],
                on_fail=Action.BLOCK,
                on_flaky=Action.BLOCK,
                on_blocked=Action.INCONCLUSIVE,
                on_not_run=Action.INCONCLUSIVE,
            ),
            "functional": GateRule(
                priorities=["P1"], on_fail=Action.BLOCK, on_flaky=Action.WARN, on_blocked=Action.WARN
            ),
            "complementary": GateRule(
                priorities=["P2"], on_fail=Action.WARN, on_flaky=Action.WARN, on_blocked=Action.WARN
            ),
        }
    )
