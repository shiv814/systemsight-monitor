from systemsight.analyzer import Thresholds, analyze_snapshot


def snapshot(cpu=10, memory=20, disk=30):
    return {
        "cpu": {"percent": cpu},
        "memory": {"percent": memory},
        "disk": {"percent": disk},
    }


def test_healthy_snapshot():
    result = analyze_snapshot(snapshot())
    assert result["status"] == "healthy"
    assert result["alerts"] == []


def test_warning_snapshot():
    result = analyze_snapshot(snapshot(cpu=91, disk=95), Thresholds(80, 85, 90))
    assert result["status"] == "warning"
    assert {item["resource"] for item in result["alerts"]} == {"cpu", "disk"}
