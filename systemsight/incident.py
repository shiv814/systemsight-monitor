"""Incident timeline generation from alert lifecycle events."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Mapping, Any
@dataclass(frozen=True, slots=True)
class TimelineEvent:
    timestamp: str; kind: str; key: str; severity: str; message: str
@dataclass(frozen=True, slots=True)
class IncidentSummary:
    key: str; opened_at: str; recovered_at: str | None; peak_severity: str; event_count: int; duration_seconds: float | None; events: tuple[TimelineEvent, ...]
def _seconds(start: str, end: str) -> float | None:
    try: return (datetime.fromisoformat(end.replace("Z", "+00:00")) - datetime.fromisoformat(start.replace("Z", "+00:00"))).total_seconds()
    except ValueError: return None
def build_incidents(events: Iterable[Mapping[str, Any]]) -> tuple[IncidentSummary, ...]:
    rank = {"info": 0, "warning": 1, "critical": 2}; grouped: dict[str, list[TimelineEvent]] = {}
    for raw in events:
        key = str(raw.get("key") or raw.get("name") or "unknown"); event = TimelineEvent(str(raw.get("timestamp", "")), str(raw.get("kind", "event")), key, str(raw.get("severity", "warning")).lower(), str(raw.get("message", ""))); grouped.setdefault(key, []).append(event)
    output: list[IncidentSummary] = []
    for key, timeline in grouped.items():
        timeline.sort(key=lambda event: event.timestamp); opened = timeline[0].timestamp; recovered = next((event.timestamp for event in reversed(timeline) if event.kind.lower() in {"recovered", "resolve", "resolved"}), None); peak = max((event.severity for event in timeline), key=lambda sev: rank.get(sev, 0), default="warning"); duration = _seconds(opened, recovered) if recovered else None; output.append(IncidentSummary(key, opened, recovered, peak, len(timeline), duration, tuple(timeline)))
    return tuple(sorted(output, key=lambda incident: incident.opened_at))
