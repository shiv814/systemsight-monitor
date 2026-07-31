import json
import threading
from urllib.request import urlopen

from systemsight.agent import MonitorAgent
from systemsight.server import create_server


def fake_collector(**kwargs):
    return {
        "timestamp": "2026-01-01T00:00:00+00:00",
        "host": "test-host",
        "cpu": {"percent": 10, "load_per_core": 0.2},
        "memory": {"percent": 20, "swap_percent": 0},
        "disk": {"percent": 30},
        "processes": {"count": 5, "top": []},
        "temperatures_c": {},
    }


def test_agent_and_http_endpoints():
    agent = MonitorAgent(collector=fake_collector)
    server = create_server("127.0.0.1", 0, agent)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base + "/snapshot") as response:
            result = json.loads(response.read())
        assert result["analysis"]["status"] == "healthy"
        with urlopen(base + "/report") as response:
            report = json.loads(response.read())
        assert report["sample_count"] == 1
        with urlopen(base + "/metrics") as response:
            metrics = response.read().decode()
        assert "systemsight_health_score 100" in metrics
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
