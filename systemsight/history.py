from __future__ import annotations

from collections import deque
import csv
import io
import json
import math
from statistics import fmean, pstdev
from typing import Any, Iterable


METRIC_PATHS = {
    "cpu_percent": ("cpu", "percent"),
    "memory_percent": ("memory", "percent"),
    "disk_percent": ("disk", "percent"),
    "swap_percent": ("memory", "swap_percent"),
    "load_per_core": ("cpu", "load_per_core"),
}


def metric_value(snapshot: dict[str, Any], metric: str) -> float | None:
    if metric not in METRIC_PATHS:
        raise KeyError(f"unknown metric: {metric}")
    value: Any = snapshot
    for key in METRIC_PATHS[metric]:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return None if value is None else float(value)


class MetricHistory:
    def __init__(self, max_samples: int = 3600, samples: Iterable[dict[str, Any]] | None = None) -> None:
        if max_samples <= 0:
            raise ValueError("max_samples must be positive")
        self.max_samples = int(max_samples)
        self._samples: deque[dict[str, Any]] = deque(maxlen=self.max_samples)
        for sample in samples or []:
            self.add(sample)

    def add(self, snapshot: dict[str, Any]) -> None:
        if "timestamp" not in snapshot:
            raise ValueError("snapshot requires a timestamp")
        self._samples.append(snapshot)

    def __len__(self) -> int:
        return len(self._samples)

    def latest(self) -> dict[str, Any] | None:
        return self._samples[-1] if self._samples else None

    def samples(self, limit: int | None = None) -> list[dict[str, Any]]:
        values = list(self._samples)
        return values if limit is None else values[-max(0, int(limit)) :]

    def summary(self, metric: str) -> dict[str, Any]:
        values = [value for snapshot in self._samples if (value := metric_value(snapshot, metric)) is not None]
        if not values:
            return {"metric": metric, "count": 0, "minimum": None, "maximum": None, "average": None, "trend": "unknown"}
        change = values[-1] - values[0]
        tolerance = max(0.5, abs(values[0]) * 0.05)
        trend = "rising" if change > tolerance else "falling" if change < -tolerance else "stable"
        return {
            "metric": metric,
            "count": len(values),
            "minimum": round(min(values), 3),
            "maximum": round(max(values), 3),
            "average": round(fmean(values), 3),
            "latest": round(values[-1], 3),
            "change": round(change, 3),
            "trend": trend,
        }

    def summaries(self) -> dict[str, dict[str, Any]]:
        return {metric: self.summary(metric) for metric in METRIC_PATHS}

    def anomalies(self, metric: str, *, window: int = 20, z_threshold: float = 2.5) -> list[dict[str, Any]]:
        if window < 3:
            raise ValueError("window must be at least 3")
        anomalies: list[dict[str, Any]] = []
        values: list[float] = []
        for snapshot in self._samples:
            current = metric_value(snapshot, metric)
            if current is None:
                continue
            baseline = values[-window:]
            if len(baseline) >= 3:
                deviation = pstdev(baseline)
                if deviation > 0:
                    z_score = (current - fmean(baseline)) / deviation
                    if abs(z_score) >= z_threshold:
                        anomalies.append({"timestamp": snapshot["timestamp"], "metric": metric, "value": round(current, 3), "z_score": round(z_score, 3)})
            values.append(current)
        return anomalies

    def to_json(self) -> str:
        return json.dumps(self.samples(), indent=2, sort_keys=True)

    @classmethod
    def from_json(cls, text: str, max_samples: int = 3600) -> "MetricHistory":
        payload = json.loads(text)
        if not isinstance(payload, list):
            raise ValueError("history JSON must be a list")
        return cls(max_samples=max_samples, samples=payload)

    def to_csv(self) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["timestamp", *METRIC_PATHS])
        for snapshot in self._samples:
            writer.writerow([snapshot.get("timestamp", ""), *[metric_value(snapshot, name) for name in METRIC_PATHS]])
        return output.getvalue()
