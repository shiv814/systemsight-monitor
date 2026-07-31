from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from .agent import MonitorAgent
from .analyzer import Thresholds
from .history import MetricHistory
from .server import create_server


def print_human(result: dict) -> None:
    snapshot = result["snapshot"]
    analysis = result["analysis"]
    print(f"SystemSight 2.0 | {snapshot['host']} | {analysis['status'].upper()} | score {analysis['health_score']}/100")
    print(f"CPU {snapshot['cpu']['percent']:.1f}% | memory {snapshot['memory']['percent']:.1f}% | disk {snapshot['disk']['percent']:.1f}% | processes {snapshot['processes']['count']}")
    if snapshot["cpu"].get("load_per_core") is not None:
        print(f"Load/core {snapshot['cpu']['load_per_core']:.2f} | uptime {snapshot['uptime_seconds']:.0f}s")
    for alert in analysis["alerts"]:
        print(f"{alert['severity'].upper()}: {alert['resource']}={alert['value']}{alert['unit']} — {alert['recommendation']}")
    for event in result["events"]:
        print(f"EVENT: {event['event']} {event['resource']} ({event['severity']})")


def build_thresholds(args: argparse.Namespace) -> Thresholds:
    return Thresholds(
        cpu_warning=args.cpu_warning,
        cpu_critical=args.cpu_critical,
        memory_warning=args.memory_warning,
        memory_critical=args.memory_critical,
        disk_warning=args.disk_warning,
        disk_critical=args.disk_critical,
    )


def add_threshold_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--cpu-warning", type=float, default=80.0)
    parser.add_argument("--cpu-critical", type=float, default=95.0)
    parser.add_argument("--memory-warning", type=float, default=85.0)
    parser.add_argument("--memory-critical", type=float, default=95.0)
    parser.add_argument("--disk-warning", type=float, default=90.0)
    parser.add_argument("--disk-critical", type=float, default=97.0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect, analyze, retain, and expose system-health metrics")
    subparsers = parser.add_subparsers(dest="command")

    snapshot = subparsers.add_parser("snapshot", help="collect one snapshot")
    snapshot.add_argument("--json", action="store_true")
    snapshot.add_argument("--disk-path", default="/")
    snapshot.add_argument("--process-limit", type=int, default=5)
    add_threshold_arguments(snapshot)

    watch = subparsers.add_parser("watch", help="continuously collect snapshots")
    watch.add_argument("--interval", type=float, default=5.0)
    watch.add_argument("--count", type=int, default=0, help="stop after N samples; 0 means unlimited")
    watch.add_argument("--json-lines", action="store_true")
    watch.add_argument("--output", type=Path, help="write retained history JSON when finished")
    watch.add_argument("--disk-path", default="/")
    watch.add_argument("--process-limit", type=int, default=5)
    add_threshold_arguments(watch)

    serve = subparsers.add_parser("serve", help="run the HTTP metrics service")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)

    report = subparsers.add_parser("report", help="summarize a saved history JSON file")
    report.add_argument("path", type=Path)
    report.add_argument("--metric", choices=["cpu_percent", "memory_percent", "disk_percent", "swap_percent", "load_per_core"])
    report.add_argument("--csv", action="store_true")

    args = parser.parse_args()
    command = args.command or "snapshot"
    if command == "serve":
        server = create_server(args.host, args.port)
        print(f"SystemSight listening on http://{args.host}:{server.server_port}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
        return
    if command == "report":
        history = MetricHistory.from_json(args.path.read_text(encoding="utf-8"))
        if args.csv:
            print(history.to_csv(), end="")
        elif args.metric:
            print(json.dumps({"summary": history.summary(args.metric), "anomalies": history.anomalies(args.metric)}, indent=2))
        else:
            print(json.dumps(history.summaries(), indent=2))
        return

    agent = MonitorAgent(thresholds=build_thresholds(args), disk_path=args.disk_path, process_limit=args.process_limit)
    if command == "snapshot":
        result = agent.sample()
        print(json.dumps(result, indent=2) if args.json else "", end="" if args.json else "")
        if not args.json:
            print_human(result)
        return
    samples = 0
    try:
        while args.count == 0 or samples < args.count:
            result = agent.sample()
            if args.json_lines:
                print(json.dumps(result, separators=(",", ":")))
            else:
                print_human(result)
            samples += 1
            if args.count == 0 or samples < args.count:
                time.sleep(max(0.1, args.interval))
    except KeyboardInterrupt:
        pass
    finally:
        if args.output:
            args.output.write_text(agent.history.to_json(), encoding="utf-8")


if __name__ == "__main__":
    main()
