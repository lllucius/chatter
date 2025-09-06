# ToolServerMetrics

Schema for tool server metrics.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**server_id** | **str** | Server ID | 
**server_name** | **str** | Server name | 
**status** | [**ServerStatus**](ServerStatus.md) |  | 
**total_tools** | **int** | Total number of tools | 
**enabled_tools** | **int** | Number of enabled tools | 
**total_calls** | **int** | Total tool calls | 
**total_errors** | **int** | Total errors | 
**success_rate** | **float** | Success rate | 
**avg_response_time_ms** | **float** |  | [optional] 
**last_activity** | **datetime** |  | [optional] 
**uptime_percentage** | **float** |  | [optional] 

## Example

```python
from chatter_sdk.models.tool_server_metrics import ToolServerMetrics

# TODO update the JSON string below
json = "{}"
# create an instance of ToolServerMetrics from a JSON string
tool_server_metrics_instance = ToolServerMetrics.from_json(json)
# print the JSON string representation of the object
print(ToolServerMetrics.to_json())

# convert the object into a dict
tool_server_metrics_dict = tool_server_metrics_instance.to_dict()
# create an instance of ToolServerMetrics from a dict
tool_server_metrics_from_dict = ToolServerMetrics.from_dict(tool_server_metrics_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


