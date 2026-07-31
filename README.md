# SystemSight Monitor

SystemSight is a cross-platform system observability toolkit for collecting host metrics, evaluating health, retaining time-series history, detecting anomalies, managing alert lifecycles, exporting reports, and exposing data over HTTP in both JSON and Prometheus-compatible formats.

The original one-shot monitor has been expanded into a reusable monitoring agent with independently testable collection, analysis, history, alerting, CLI, and server layers.

## Capabilities

### Rich host snapshots

- aggregate and per-core CPU utilization
- load average normalized by logical core count
- physical and logical core inventory
- memory, available memory, and swap pressure
- disk utilization, free space, and cumulative I/O bytes
- network bytes, packets, and error counters
- system uptime, platform, Python version, and hostname
- sensor temperatures when available
- ranked CPU/memory process summaries

### Health analysis

Each monitored resource has warning and critical thresholds. An analysis returns:

- overall `healthy`, `warning`, or `critical` status
- a 0-100 health score
- structured alerts with value, units, thresholds, and severity
- practical remediation recommendations

### Time-series history

`MetricHistory` retains a bounded rolling window, calculates minimum/maximum/average/latest/change/trend summaries, detects z-score anomalies, and exports or restores JSON and CSV.

### Stateful alerting

`AlertStateMachine` turns repeated samples into meaningful events:

- `opened` when a resource first becomes unhealthy
- `escalated` when warning becomes critical
- rate-limited `reminder` events after a configurable cooldown
- `recovered` when a resource returns to normal

### HTTP observability service

| Route | Purpose |
|---|---|
| `/health` | Current service and host status |
| `/snapshot` | Collect and return a fresh sample |
| `/history?limit=100` | Retrieve recent snapshots |
| `/report` | Latest result, summaries, and active alerts |
| `/metrics` | Prometheus-compatible gauge output |

## Install

```bash
python -m pip install -r requirements.txt
```

## CLI

Collect a single human-readable snapshot:

```bash
python -m systemsight.cli snapshot
```

Print full JSON:

```bash
python -m systemsight.cli snapshot --json --process-limit 10
```

Watch five samples, one second apart, then save the history:

```bash
python -m systemsight.cli watch --interval 1 --count 5 --output history.json
```

Analyze a saved history:

```bash
python -m systemsight.cli report history.json
python -m systemsight.cli report history.json --metric cpu_percent
python -m systemsight.cli report history.json --csv
```

Run the HTTP service:

```bash
python -m systemsight.cli serve --host 0.0.0.0 --port 8765
curl http://127.0.0.1:8765/snapshot
curl http://127.0.0.1:8765/metrics
```

## Library usage

```python
from systemsight import MonitorAgent, Thresholds

agent = MonitorAgent(
    thresholds=Thresholds(cpu_warning=70, cpu_critical=90),
    history_size=720,
    alert_cooldown=120,
)

result = agent.sample()
print(result["analysis"]["health_score"])
print(agent.report()["summaries"])
```

## Architecture

```text
systemsight/
├── collector.py  # cross-platform psutil measurements
├── analyzer.py   # thresholds, severity, scores, recommendations
├── history.py    # bounded time series, trends, anomalies, exports
├── alerts.py     # open/escalate/remind/recover state machine
├── agent.py      # orchestration and reusable monitoring session
├── server.py     # JSON and Prometheus HTTP endpoints
└── cli.py        # snapshot, watch, report, and serve commands
```

## Test

```bash
python -m pip install -r requirements.txt pytest
python -m pytest
```

Tests cover threshold validation, warning/critical classification, health scoring, bounded retention, trend calculation, JSON round trips, CSV export, anomaly detection, alert cooldown and recovery, agent orchestration, and live HTTP endpoints with a deterministic fake collector.
