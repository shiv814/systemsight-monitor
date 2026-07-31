from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Thresholds:
    cpu_warning: float = 80.0
    cpu_critical: float = 95.0
    memory_warning: float = 85.0
    memory_critical: float = 95.0
    disk_warning: float = 90.0
    disk_critical: float = 97.0
    swap_warning: float = 60.0
    swap_critical: float = 90.0
    load_warning: float = 1.0
    load_critical: float = 2.0
    temperature_warning: float = 80.0
    temperature_critical: float = 95.0

    def __post_init__(self) -> None:
        for name, value in self.__dict__.items():
            if float(value) < 0:
                raise ValueError(f"{name} cannot be negative")
        pairs = [
            ("cpu", self.cpu_warning, self.cpu_critical),
            ("memory", self.memory_warning, self.memory_critical),
            ("disk", self.disk_warning, self.disk_critical),
            ("swap", self.swap_warning, self.swap_critical),
            ("load", self.load_warning, self.load_critical),
            ("temperature", self.temperature_warning, self.temperature_critical),
        ]
        for name, warning, critical in pairs:
            if warning > critical:
                raise ValueError(f"{name} warning threshold cannot exceed critical threshold")


def _maximum_temperature(snapshot: dict[str, Any]) -> float | None:
    values = [float(value) for group in snapshot.get("temperatures_c", {}).values() for value in group]
    return max(values) if values else None


def _resource_checks(snapshot: dict[str, Any], thresholds: Thresholds) -> list[tuple[str, float, float, float, str]]:
    checks = [
        ("cpu", float(snapshot["cpu"]["percent"]), thresholds.cpu_warning, thresholds.cpu_critical, "%"),
        ("memory", float(snapshot["memory"]["percent"]), thresholds.memory_warning, thresholds.memory_critical, "%"),
        ("disk", float(snapshot["disk"]["percent"]), thresholds.disk_warning, thresholds.disk_critical, "%"),
        ("swap", float(snapshot.get("memory", {}).get("swap_percent", 0.0)), thresholds.swap_warning, thresholds.swap_critical, "%"),
    ]
    load = snapshot.get("cpu", {}).get("load_per_core")
    if load is not None:
        checks.append(("load_per_core", float(load), thresholds.load_warning, thresholds.load_critical, "ratio"))
    temperature = _maximum_temperature(snapshot)
    if temperature is not None:
        checks.append(("temperature", temperature, thresholds.temperature_warning, thresholds.temperature_critical, "°C"))
    return checks


def _recommendation(resource: str, severity: str) -> str:
    prefix = "Immediately" if severity == "critical" else "Consider"
    recommendations = {
        "cpu": f"{prefix} inspect CPU-heavy processes and sustained workload.",
        "memory": f"{prefix} inspect memory-heavy processes and application leaks.",
        "disk": f"{prefix} free disk space, rotate logs, or expand storage.",
        "swap": f"{prefix} reduce memory pressure to avoid swap thrashing.",
        "load_per_core": f"{prefix} reduce queued work or add compute capacity.",
        "temperature": f"{prefix} verify cooling, airflow, and fan operation.",
    }
    return recommendations[resource]


def analyze_snapshot(snapshot: dict[str, Any], thresholds: Thresholds | None = None) -> dict[str, Any]:
    thresholds = thresholds or Thresholds()
    alerts: list[dict[str, Any]] = []
    for resource, value, warning, critical, unit in _resource_checks(snapshot, thresholds):
        severity = "critical" if value >= critical else "warning" if value >= warning else None
        if severity:
            alerts.append(
                {
                    "resource": resource,
                    "value": round(value, 2),
                    "unit": unit,
                    "threshold": critical if severity == "critical" else warning,
                    "warning_threshold": warning,
                    "critical_threshold": critical,
                    "severity": severity,
                    "recommendation": _recommendation(resource, severity),
                }
            )
    status = "critical" if any(item["severity"] == "critical" for item in alerts) else "warning" if alerts else "healthy"
    penalty = sum(25 if item["severity"] == "critical" else 10 for item in alerts)
    return {
        "status": status,
        "health_score": max(0, 100 - penalty),
        "alerts": alerts,
        "alert_count": len(alerts),
        "checked_resources": len(_resource_checks(snapshot, thresholds)),
        "recommendations": [item["recommendation"] for item in alerts],
    }
