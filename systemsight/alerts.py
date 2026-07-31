from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass
class AlertEvent:
    resource: str
    severity: str
    event: str
    timestamp: str
    value: float | None
    message: str

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


class AlertStateMachine:
    """Converts repeated analyses into useful open/escalate/recover events."""

    def __init__(self, cooldown_seconds: float = 300.0) -> None:
        if cooldown_seconds < 0:
            raise ValueError("cooldown_seconds cannot be negative")
        self.cooldown_seconds = float(cooldown_seconds)
        self._active: dict[str, str] = {}
        self._last_emitted: dict[tuple[str, str], float] = {}

    @staticmethod
    def _epoch(timestamp: str | None) -> float:
        if timestamp is None:
            return datetime.now(timezone.utc).timestamp()
        return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).timestamp()

    def evaluate(self, analysis: dict[str, Any], *, timestamp: str | None = None) -> list[dict[str, Any]]:
        moment = timestamp or datetime.now(timezone.utc).isoformat()
        epoch = self._epoch(moment)
        current = {item["resource"]: item for item in analysis.get("alerts", [])}
        events: list[AlertEvent] = []

        for resource, alert in current.items():
            severity = alert["severity"]
            previous = self._active.get(resource)
            event = "opened" if previous is None else "escalated" if previous == "warning" and severity == "critical" else "reminder"
            key = (resource, severity)
            can_emit = event != "reminder" or epoch - self._last_emitted.get(key, float("-inf")) >= self.cooldown_seconds
            if can_emit:
                events.append(AlertEvent(resource, severity, event, moment, float(alert["value"]), f"{resource} is {severity} at {alert['value']}{alert.get('unit', '')}"))
                self._last_emitted[key] = epoch
            self._active[resource] = severity

        for resource in sorted(set(self._active) - set(current)):
            previous = self._active.pop(resource)
            events.append(AlertEvent(resource, "healthy", "recovered", moment, None, f"{resource} recovered from {previous}"))

        return [event.as_dict() for event in events]

    def active(self) -> dict[str, str]:
        return dict(self._active)
