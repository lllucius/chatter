# DashboardResponse

Schema for analytics dashboard response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**conversation_stats** | [**ConversationStatsResponse**](ConversationStatsResponse.md) |  | 
**usage_metrics** | [**UsageMetricsResponse**](UsageMetricsResponse.md) |  | 
**performance_metrics** | [**PerformanceMetricsResponse**](PerformanceMetricsResponse.md) |  | 
**document_analytics** | [**DocumentAnalyticsResponse**](DocumentAnalyticsResponse.md) |  | 
**system_health** | [**SystemAnalyticsResponse**](SystemAnalyticsResponse.md) |  | 
**custom_metrics** | **List[Dict[str, object]]** | Custom metrics | 
**generated_at** | **datetime** | Dashboard generation time | 

## Example

```python
from chatter_sdk.models.dashboard_response import DashboardResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DashboardResponse from a JSON string
dashboard_response_instance = DashboardResponse.from_json(json)
# print the JSON string representation of the object
print(DashboardResponse.to_json())

# convert the object into a dict
dashboard_response_dict = dashboard_response_instance.to_dict()
# create an instance of DashboardResponse from a dict
dashboard_response_from_dict = DashboardResponse.from_dict(dashboard_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


