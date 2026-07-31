import pytest

from systemsight.analyzer import Thresholds, analyze_snapshot


def snapshot(cpu=10, memory=20, disk=30, swap=0, load=0.1, temperatures=None):
    return {
        "cpu": {"percent": cpu, "load_per_core": load},
        "memory": {"percent": memory, "swap_percent": swap},
        "disk": {"percent": disk},
        "temperatures_c": temperatures or {},
    }


def test_healthy_snapshot_has_full_score():
    result = analyze_snapshot(snapshot())
    assert result["status"] == "healthy"
    assert result["health_score"] == 100
    assert result["alerts"] == []


def test_warning_and_critical_resources():
    result = analyze_snapshot(snapshot(cpu=85, disk=99, temperatures={"core": [82]}))
    assert result["status"] == "critical"
    by_resource = {item["resource"]: item for item in result["alerts"]}
    assert by_resource["cpu"]["severity"] == "warning"
    assert by_resource["disk"]["severity"] == "critical"
    assert by_resource["temperature"]["severity"] == "warning"
    assert result["health_score"] == 55


def test_threshold_validation():
    with pytest.raises(ValueError):
        Thresholds(cpu_warning=95, cpu_critical=90)
