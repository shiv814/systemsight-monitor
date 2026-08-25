# Contributing

- keep OS-specific collection isolated in `collector.py`
- keep analytical logic independent from `psutil` where possible
- add deterministic tests for rules, forecasts or lifecycle behaviour
- run `python -m compileall systemsight`, `python -m pytest -q` and `python -m systemsight.demo`
- preserve Linux/Windows/macOS compatibility
