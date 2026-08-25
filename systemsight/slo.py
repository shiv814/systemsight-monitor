"""Service-level objective and error-budget calculations."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class SLO:
    name: str; target: float; window_minutes: int
    def __post_init__(self) -> None:
        if not 0 < self.target < 1: raise ValueError("target must be between 0 and 1")
        if self.window_minutes <= 0: raise ValueError("window_minutes must be positive")
@dataclass(frozen=True, slots=True)
class ErrorBudget:
    objective: str; target: float; total_events: int; bad_events: int; allowed_bad_events: float; remaining_bad_events: float; burn_rate: float; compliance: float; exhausted: bool

def evaluate_error_budget(slo: SLO, *, total_events: int, bad_events: int) -> ErrorBudget:
    if total_events < 0 or bad_events < 0 or bad_events > total_events: raise ValueError("invalid event counts")
    if total_events == 0: return ErrorBudget(slo.name, slo.target, 0, 0, 0.0, 0.0, 0.0, 1.0, False)
    allowed = total_events * (1.0 - slo.target); remaining = allowed - bad_events; burn = bad_events / allowed if allowed > 0 else float("inf"); compliance = 1.0 - (bad_events / total_events)
    return ErrorBudget(slo.name, slo.target, total_events, bad_events, allowed, remaining, burn, compliance, remaining < 0)

def multi_window_burn_rate(short: ErrorBudget, long: ErrorBudget) -> float:
    if short.target != long.target: raise ValueError("budgets must use the same SLO target")
    return max(short.burn_rate, long.burn_rate)
