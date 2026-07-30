from __future__ import annotations

import argparse
import json
import time

from .analyzer import Thresholds, analyze_snapshot
from .collector import collect_snapshot


def print_human(snapshot, analysis):
    print(f"SystemSight - {snapshot['host']} - {analysis['status'].upper()}")
    print(f"CPU: {snapshot['cpu']['percent']:.1f}%")
    print(f"Memory: {snapshot['memory']['percent']:.1f}% ({snapshot['memory']['used_gib']} / {snapshot['memory']['total_gib']} GiB)")
    print(f"Disk: {snapshot['disk']['percent']:.1f}% ({snapshot['disk']['used_gib']} / {snapshot['disk']['total_gib']} GiB)")
    for alert in analysis["alerts"]:
        print(f"WARNING: {alert['resource']} at {alert['value']:.1f}% (threshold {alert['threshold']:.1f}%)")


def main():
    parser = argparse.ArgumentParser(description="Collect and evaluate system-health metrics")
    parser.add_argument("--json", action="store_true", help="print JSON output")
    parser.add_argument("--watch", type=float, metavar="SECONDS", help="repeat at an interval")
    parser.add_argument("--cpu-warning", type=float, default=80.0)
    parser.add_argument("--memory-warning", type=float, default=85.0)
    parser.add_argument("--disk-warning", type=float, default=90.0)
    args = parser.parse_args()
    thresholds = Thresholds(args.cpu_warning, args.memory_warning, args.disk_warning)
    while True:
        snapshot = collect_snapshot()
        analysis = analyze_snapshot(snapshot, thresholds)
        if args.json:
            print(json.dumps({"snapshot": snapshot, "analysis": analysis}, indent=2))
        else:
            print_human(snapshot, analysis)
        if not args.watch:
            break
        time.sleep(max(args.watch, 0.1))


if __name__ == "__main__":
    main()
