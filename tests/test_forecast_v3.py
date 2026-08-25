from systemsight.forecast import ewma, linear_forecast, project_threshold, rolling_zscore

def test_forecast_and_capacity_projection():
    values=[10,20,30,40,50]; forecast=linear_forecast(values,2); assert round(forecast.forecast)==70; assert forecast.r_squared>.99; projection=project_threshold(values,80); assert 2.9 < projection.samples_until_threshold < 3.1; assert ewma([10,20],.5)==15; assert rolling_zscore([10,10,10,20]) > 0
