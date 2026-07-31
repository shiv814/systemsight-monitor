"""SystemSight monitoring and alerting toolkit."""

from .agent import MonitorAgent
from .analyzer import Thresholds, analyze_snapshot
from .collector import collect_snapshot
from .history import MetricHistory

__all__ = ["MetricHistory", "MonitorAgent", "Thresholds", "analyze_snapshot", "collect_snapshot"]
__version__ = "2.0.0"
