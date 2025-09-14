# ChartReadyAnalytics

Schema for chart-ready analytics data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**conversation_chart_data** | [**List[TimeSeriesDataPoint]**](TimeSeriesDataPoint.md) | Daily conversation data for charts | 
**token_usage_data** | [**List[TimeSeriesDataPoint]**](TimeSeriesDataPoint.md) | Token usage over time for charts | 
**performance_chart_data** | [**List[ChartDataPoint]**](ChartDataPoint.md) | Performance metrics for charts | 
**system_health_data** | [**List[ChartDataPoint]**](ChartDataPoint.md) | System health data for charts | 
**integration_data** | [**List[ChartDataPoint]**](ChartDataPoint.md) | Integration usage data for charts | 
**hourly_performance_data** | **List[Dict[str, object]]** | 24-hour performance breakdown | 

## Example

```python
from chatter_sdk.models.chart_ready_analytics import ChartReadyAnalytics

# TODO update the JSON string below
json = "{}"
# create an instance of ChartReadyAnalytics from a JSON string
chart_ready_analytics_instance = ChartReadyAnalytics.from_json(json)
# print the JSON string representation of the object
print(ChartReadyAnalytics.to_json())

# convert the object into a dict
chart_ready_analytics_dict = chart_ready_analytics_instance.to_dict()
# create an instance of ChartReadyAnalytics from a dict
chart_ready_analytics_from_dict = ChartReadyAnalytics.from_dict(chart_ready_analytics_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


