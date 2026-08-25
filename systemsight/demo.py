"""Offline SystemSight v3 feature demonstration."""
from __future__ import annotations
from pathlib import Path
from dataclasses import asdict
from .fleet import summarize_fleet
from .forecast import linear_forecast, project_threshold
from .report import build_report
from .rules import MetricRule, Operator, RuleSet
from .slo import SLO, evaluate_error_budget

def main() -> None:
    snapshots = [{"host":"edge-a","cpu":{"percent":42},"memory":{"percent":63},"disk":{"percent":71}}, {"host":"edge-b","cpu":{"percent":78},"memory":{"percent":69},"disk":{"percent":66}}, {"host":"edge-c","cpu":{"percent":55},"memory":{"percent":74},"disk":{"percent":82}}]
    rules = RuleSet([MetricRule("cpu-hot","cpu.percent",Operator.GTE,75,"warning"), MetricRule("disk-critical","disk.percent",Operator.GTE,90,"critical")]); active = rules.triggered(snapshots[1]); trend = [35,39,44,48,53,58,62]
    print("forecast:", linear_forecast(trend, horizon=3)); print("capacity:", project_threshold(trend, 85)); print("fleet:", summarize_fleet(snapshots)); print("error budget:", evaluate_error_budget(SLO("availability",.999,30*24*60), total_events=100_000,bad_events=35))
    Path("systemsight-demo.html").write_text(build_report(snapshots[1], {"cpu.percent":trend}, [asdict(r) for r in active]), encoding="utf-8"); print("Generated systemsight-demo.html")
if __name__ == "__main__": main()
