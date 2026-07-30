# SystemSight Monitor

SystemSight is a cross-platform command-line health monitor that collects CPU, memory, disk, network, and available temperature data, then evaluates the snapshot against configurable thresholds.

## Features

- Human-readable and JSON output modes
- Continuous watch mode for repeated snapshots
- Configurable CPU, memory, and disk warning levels
- Pure analysis layer separated from metric collection for easy testing
- Automated tests and GitHub Actions

## Run

```bash
python -m pip install -r requirements.txt
python -m systemsight.cli
python -m systemsight.cli --json
python -m systemsight.cli --watch 5 --cpu-warning 75
```

## Test

```bash
python -m pytest
```
