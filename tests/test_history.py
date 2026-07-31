import json

from systemsight.history import MetricHistory


def sample(index, cpu):
    return {
        "timestamp": f"2026-01-01T00:00:{index:02d}+00:00",
        "cpu": {"percent": cpu, "load_per_core": 0.1},
        "memory": {"percent": 40, "swap_percent": 0},
        "disk": {"percent": 50},
    }


def test_history_summary_retention_and_roundtrip():
    history = MetricHistory(max_samples=3)
    for index, cpu in enumerate([10, 20, 30, 40]):
        history.add(sample(index, cpu))
    assert len(history) == 3
    summary = history.summary("cpu_percent")
    assert summary["minimum"] == 20
    assert summary["maximum"] == 40
    assert summary["trend"] == "rising"
    restored = MetricHistory.from_json(history.to_json())
    assert restored.summary("cpu_percent")["average"] == 30
    assert "cpu_percent" in history.to_csv().splitlines()[0]


def test_anomaly_detection():
    history = MetricHistory()
    for index, cpu in enumerate([10, 11, 9, 10, 10, 80]):
        history.add(sample(index, cpu))
    anomalies = history.anomalies("cpu_percent", window=5, z_threshold=3)
    assert len(anomalies) == 1
    assert anomalies[0]["value"] == 80
