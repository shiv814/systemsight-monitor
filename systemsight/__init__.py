"""SystemSight monitoring and alerting toolkit."""
from .agent import MonitorAgent
from .analyzer import Thresholds, analyze_snapshot
from .collector import collect_snapshot
from .history import MetricHistory
from .rules import MetricRule, Operator, RuleSet
from .forecast import Forecast, linear_forecast, project_threshold
from .slo import SLO, evaluate_error_budget
__all__ = ["MetricHistory","MonitorAgent","Thresholds","analyze_snapshot","collect_snapshot","MetricRule","Operator","RuleSet","Forecast","linear_forecast","project_threshold","SLO","evaluate_error_budget"]
__version__ = "3.0.0"
