from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Thresholds:
    cpu_warning: float = 80.0
    memory_warning: float = 85.0
    disk_warning: float = 90.0


def analyze_snapshot(snapshot: dict[str, Any], thresholds: Thresholds | None = None) -> dict[str, Any]:
    thresholds = thresholds or Thresholds()
    checks = {
        "cpu": (float(snapshot["cpu"]["percent"]), thresholds.cpu_warning),
        "memory": (float(snapshot["memory"]["percent"]), thresholds.memory_warning),
        "disk": (float(snapshot["disk"]["percent"]), thresholds.disk_warning),
    }
    alerts = [
        {"resource": name, "value": value, "threshold": threshold, "severity": "warning"}
        for name, (value, threshold) in checks.items()
        if value >= threshold
    ]
    return {
        "status": "warning" if alerts else "healthy",
        "alerts": alerts,
        "checked_resources": len(checks),
    }
