from systemsight.rules import MetricRule, Operator, RuleSet, metric_value

def test_nested_rule_evaluation():
    snapshot = {"cpu":{"percent":91.0},"memory":{"percent":40.0}}; rules = RuleSet([MetricRule("hot","cpu.percent",Operator.GTE,90,"critical"), MetricRule("mem","memory.percent",Operator.GT,80)]); results = rules.evaluate(snapshot)
    assert results[0].triggered is True; assert results[1].triggered is False; assert metric_value(snapshot,"cpu.percent") == 91.0; assert rules.triggered(snapshot,minimum_severity="critical")[0].name == "hot"
