from systemsight.slo import SLO, evaluate_error_budget
from systemsight.fleet import summarize_fleet

def test_slo_error_budget_and_fleet():
    budget=evaluate_error_budget(SLO("api",.99,60),total_events=1000,bad_events=5); assert budget.exhausted is False; assert budget.burn_rate < 1; fleet=summarize_fleet([{"host":"a","cpu":{"percent":20}},{"host":"b","cpu":{"percent":80}}],paths=("cpu.percent",)); assert fleet.host_count==2; assert fleet.hottest_host=="b"; assert fleet.metrics[0].average==50
