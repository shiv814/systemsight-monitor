"""Small, dependency-free forecasting primitives for metric histories."""
from __future__ import annotations
from dataclasses import dataclass
from math import sqrt
from statistics import fmean
from typing import Iterable

@dataclass(frozen=True, slots=True)
class Forecast:
    latest: float; forecast: float; slope_per_sample: float; r_squared: float; samples: int
@dataclass(frozen=True, slots=True)
class CapacityProjection:
    threshold: float; current: float; slope_per_sample: float; samples_until_threshold: float | None; status: str

def linear_forecast(values: Iterable[float], horizon: int = 1) -> Forecast:
    series = [float(v) for v in values]
    if not series: raise ValueError("at least one sample is required")
    if horizon < 0: raise ValueError("horizon cannot be negative")
    if len(series) == 1: return Forecast(series[-1], series[-1], 0.0, 1.0, 1)
    n = len(series); x_mean = (n - 1) / 2.0; y_mean = fmean(series)
    numerator = sum((i - x_mean) * (value - y_mean) for i, value in enumerate(series)); denominator = sum((i - x_mean) ** 2 for i in range(n))
    slope = numerator / denominator if denominator else 0.0; intercept = y_mean - slope * x_mean; predicted = intercept + slope * (n - 1 + horizon)
    total = sum((value - y_mean) ** 2 for value in series); residual = sum((value - (intercept + slope * i)) ** 2 for i, value in enumerate(series))
    r2 = 1.0 if total == 0 else max(0.0, 1.0 - residual / total)
    return Forecast(series[-1], predicted, slope, r2, n)

def ewma(values: Iterable[float], alpha: float = 0.3) -> float:
    if not 0 < alpha <= 1: raise ValueError("alpha must be in (0, 1]")
    iterator = iter(float(v) for v in values)
    try: estimate = next(iterator)
    except StopIteration as exc: raise ValueError("at least one sample is required") from exc
    for value in iterator: estimate = alpha * value + (1 - alpha) * estimate
    return estimate

def rolling_zscore(values: Iterable[float]) -> float | None:
    series = [float(v) for v in values]
    if len(series) < 3: return None
    reference = series[:-1]; mean = fmean(reference); variance = fmean((value - mean) ** 2 for value in reference); std = sqrt(variance)
    if std == 0:
        if series[-1] == mean: return 0.0
        return float("inf") if series[-1] > mean else float("-inf")
    return (series[-1] - mean) / std

def project_threshold(values: Iterable[float], threshold: float) -> CapacityProjection:
    forecast = linear_forecast(values, horizon=0); slope = forecast.slope_per_sample; current = forecast.latest
    if current >= threshold: return CapacityProjection(threshold, current, slope, 0.0, "threshold-reached")
    if slope <= 0: return CapacityProjection(threshold, current, slope, None, "stable-or-improving")
    remaining = (threshold - current) / slope
    return CapacityProjection(threshold, current, slope, remaining, "approaching" if remaining <= 10 else "growing")
