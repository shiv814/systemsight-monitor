"""Composable metric-rule evaluation for SystemSight."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Mapping

class Operator(str, Enum):
    GT = ">"; GTE = ">="; LT = "<"; LTE = "<="; EQ = "=="; NE = "!="

@dataclass(frozen=True, slots=True)
class MetricRule:
    name: str
    path: str
    operator: Operator
    threshold: float
    severity: str = "warning"
    description: str = ""
    def __post_init__(self) -> None:
        if not self.name.strip(): raise ValueError("rule name is required")
        if not self.path.strip(): raise ValueError("metric path is required")
        severity = self.severity.strip().lower()
        if severity not in {"info", "warning", "critical"}: raise ValueError("severity must be info, warning, or critical")
        object.__setattr__(self, "severity", severity)

@dataclass(frozen=True, slots=True)
class RuleResult:
    name: str; path: str; severity: str; value: float | None; threshold: float; operator: str; triggered: bool; message: str

def metric_value(snapshot: Mapping[str, Any], path: str) -> Any:
    value: Any = snapshot
    for part in path.split("."):
        if isinstance(value, Mapping) and part in value: value = value[part]
        else: return None
    return value

def _compare(value: float, operator: Operator, threshold: float) -> bool:
    return {Operator.GT: value > threshold, Operator.GTE: value >= threshold, Operator.LT: value < threshold, Operator.LTE: value <= threshold, Operator.EQ: value == threshold, Operator.NE: value != threshold}[operator]

class RuleSet:
    def __init__(self, rules: Iterable[MetricRule] = ()):
        self.rules = tuple(rules)
        names = [rule.name for rule in self.rules]
        if len(names) != len(set(names)): raise ValueError("rule names must be unique")
    def evaluate(self, snapshot: Mapping[str, Any]) -> tuple[RuleResult, ...]:
        results: list[RuleResult] = []
        for rule in self.rules:
            raw = metric_value(snapshot, rule.path)
            try: numeric = float(raw) if raw is not None else None
            except (TypeError, ValueError): numeric = None
            triggered = numeric is not None and _compare(numeric, rule.operator, rule.threshold)
            message = f"{rule.path} unavailable" if numeric is None else f"{rule.path}={numeric:g} {rule.operator.value} {rule.threshold:g} · {'triggered' if triggered else 'ok'}"
            results.append(RuleResult(rule.name, rule.path, rule.severity, numeric, rule.threshold, rule.operator.value, triggered, message))
        return tuple(results)
    def triggered(self, snapshot: Mapping[str, Any], *, minimum_severity: str = "info") -> tuple[RuleResult, ...]:
        rank = {"info": 0, "warning": 1, "critical": 2}; minimum = rank[minimum_severity.lower()]
        return tuple(result for result in self.evaluate(snapshot) if result.triggered and rank[result.severity] >= minimum)
