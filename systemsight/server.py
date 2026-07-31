from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .agent import MonitorAgent


class SystemSightHandler(BaseHTTPRequestHandler):
    agent = MonitorAgent()
    server_version = "SystemSight/2.0"

    def log_message(self, format: str, *args: object) -> None:
        return

    def _json(self, status: int, payload: object) -> None:
        encoded = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _text(self, status: int, payload: str, content_type: str = "text/plain; charset=utf-8") -> None:
        encoded = payload.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        if parsed.path == "/health":
            latest = self.agent.last_result or self.agent.sample()
            self._json(HTTPStatus.OK, {"service": "systemsight", "version": "2.0", "status": latest["analysis"]["status"]})
            return
        if parsed.path == "/snapshot":
            self._json(HTTPStatus.OK, self.agent.sample())
            return
        if parsed.path == "/history":
            limit = int(query.get("limit", [100])[0])
            self._json(HTTPStatus.OK, {"count": len(self.agent.history), "samples": self.agent.history.samples(limit)})
            return
        if parsed.path == "/report":
            if self.agent.last_result is None:
                self.agent.sample()
            self._json(HTTPStatus.OK, self.agent.report())
            return
        if parsed.path == "/metrics":
            latest = self.agent.last_result or self.agent.sample()
            snapshot = latest["snapshot"]
            analysis = latest["analysis"]
            lines = [
                "# HELP systemsight_resource_percent Current resource utilization percentage.",
                "# TYPE systemsight_resource_percent gauge",
                f'systemsight_resource_percent{{resource="cpu"}} {snapshot["cpu"]["percent"]}',
                f'systemsight_resource_percent{{resource="memory"}} {snapshot["memory"]["percent"]}',
                f'systemsight_resource_percent{{resource="disk"}} {snapshot["disk"]["percent"]}',
                f'systemsight_health_score {analysis["health_score"]}',
                f'systemsight_active_alerts {analysis["alert_count"]}',
            ]
            self._text(HTTPStatus.OK, "\n".join(lines) + "\n", "text/plain; version=0.0.4; charset=utf-8")
            return
        self._json(HTTPStatus.NOT_FOUND, {"error": "route not found"})


def create_server(host: str = "127.0.0.1", port: int = 8765, agent: MonitorAgent | None = None) -> ThreadingHTTPServer:
    handler = type("ConfiguredSystemSightHandler", (SystemSightHandler,), {"agent": agent or MonitorAgent()})
    return ThreadingHTTPServer((host, port), handler)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve SystemSight health data over HTTP")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = create_server(args.host, args.port)
    print(f"SystemSight listening on http://{args.host}:{server.server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
