"""Fleet-level aggregation over independent host snapshots."""
from __future__ import annotations
from dataclasses import dataclass
from statistics import fmean
from typing import Any, Iterable, Mapping

def _get(snapshot: Mapping[str, Any], path: str) -> float | None:
    value: Any = snapshot
    for part in path.split("."):
        if not isinstance(value, Mapping) or part not in value: return None
        value = value[part]
    try: return float(value)
    except (TypeError, ValueError): return None
@dataclass(frozen=True, slots=True)
class FleetMetric:
    path: str; hosts_reporting: int; minimum: float; maximum: float; average: float; spread: float
@dataclass(frozen=True, slots=True)
class FleetSummary:
    host_count: int; metrics: tuple[FleetMetric, ...]; hottest_host: str | None; hottest_cpu: float | None

def summarize_fleet(snapshots: Iterable[Mapping[str, Any]], paths: Iterable[str] = ("cpu.percent", "memory.percent", "disk.percent")) -> FleetSummary:
    items = list(snapshots); metrics: list[FleetMetric] = []
    for path in paths:
        values = [value for item in items if (value := _get(item, path)) is not None]
        if values: metrics.append(FleetMetric(path, len(values), min(values), max(values), fmean(values), max(values) - min(values)))
    hottest_name = None; hottest_cpu = None
    for item in items:
        cpu = _get(item, "cpu.percent")
        if cpu is not None and (hottest_cpu is None or cpu > hottest_cpu): hottest_cpu = cpu; hottest_name = str(item.get("host") or item.get("hostname") or "unknown")
    return FleetSummary(len(items), tuple(metrics), hottest_name, hottest_cpu)
