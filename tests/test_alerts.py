from systemsight.alerts import AlertStateMachine


def analysis(*alerts):
    return {"alerts": list(alerts)}


def alert(resource, severity, value=90):
    return {"resource": resource, "severity": severity, "value": value, "unit": "%"}


def test_alert_lifecycle_and_cooldown():
    machine = AlertStateMachine(cooldown_seconds=60)
    opened = machine.evaluate(analysis(alert("cpu", "warning")), timestamp="2026-01-01T00:00:00+00:00")
    assert opened[0]["event"] == "opened"
    assert machine.evaluate(analysis(alert("cpu", "warning")), timestamp="2026-01-01T00:00:30+00:00") == []
    escalated = machine.evaluate(analysis(alert("cpu", "critical", 99)), timestamp="2026-01-01T00:00:31+00:00")
    assert escalated[0]["event"] == "escalated"
    recovered = machine.evaluate(analysis(), timestamp="2026-01-01T00:00:40+00:00")
    assert recovered[0]["event"] == "recovered"
