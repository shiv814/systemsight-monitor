from __future__ import annotations

from typing import Any, Callable

from .alerts import AlertStateMachine
from .analyzer import Thresholds, analyze_snapshot
from .collector import collect_snapshot
from .history import MetricHistory


class MonitorAgent:
    def __init__(
        self,
        *,
        collector: Callable[..., dict[str, Any]] = collect_snapshot,
        thresholds: Thresholds | None = None,
        history_size: int = 3600,
        alert_cooldown: float = 300.0,
        disk_path: str = "/",
        process_limit: int = 5,
    ) -> None:
        self.collector = collector
        self.thresholds = thresholds or Thresholds()
        self.history = MetricHistory(history_size)
        self.alerts = AlertStateMachine(alert_cooldown)
        self.disk_path = disk_path
        self.process_limit = process_limit
        self.last_result: dict[str, Any] | None = None

    def sample(self) -> dict[str, Any]:
        snapshot = self.collector(disk_path=self.disk_path, process_limit=self.process_limit)
        analysis = analyze_snapshot(snapshot, self.thresholds)
        events = self.alerts.evaluate(analysis, timestamp=snapshot["timestamp"])
        self.history.add(snapshot)
        self.last_result = {"snapshot": snapshot, "analysis": analysis, "events": events}
        return self.last_result

    def report(self) -> dict[str, Any]:
        return {
            "sample_count": len(self.history),
            "latest": self.last_result,
            "summaries": self.history.summaries(),
            "active_alerts": self.alerts.active(),
        }
