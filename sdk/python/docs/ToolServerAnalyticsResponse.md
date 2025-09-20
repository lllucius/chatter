# ToolServerAnalyticsResponse

Schema for tool server analytics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_requests** | **int** | Total requests processed | 
**successful_requests** | **int** | Successful requests | 
**failed_requests** | **int** | Failed requests | 
**average_response_time_ms** | **float** | Average response time in milliseconds | 
**tool_usage_stats** | **Dict[str, int]** | Tool usage statistics | 
**server_uptime_stats** | **Dict[str, object]** | Server uptime statistics | 
**error_distribution** | **Dict[str, int]** | Error distribution by type | 

## Example

```python
from chatter_sdk.models.tool_server_analytics_response import ToolServerAnalyticsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ToolServerAnalyticsResponse from a JSON string
tool_server_analytics_response_instance = ToolServerAnalyticsResponse.from_json(json)
# print the JSON string representation of the object
print(ToolServerAnalyticsResponse.to_json())

# convert the object into a dict
tool_server_analytics_response_dict = tool_server_analytics_response_instance.to_dict()
# create an instance of ToolServerAnalyticsResponse from a dict
tool_server_analytics_response_from_dict = ToolServerAnalyticsResponse.from_dict(tool_server_analytics_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


