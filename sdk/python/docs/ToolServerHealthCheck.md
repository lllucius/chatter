# ToolServerHealthCheck

Schema for tool server health check.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**server_id** | **str** | Server ID | 
**server_name** | **str** | Server name | 
**status** | [**ServerStatus**](ServerStatus.md) |  | 
**is_running** | **bool** | Whether server is running | 
**is_responsive** | **bool** | Whether server is responsive | 
**tools_count** | **int** | Number of available tools | 
**last_check** | **datetime** | Last health check time | 
**error_message** | **str** |  | [optional] 

## Example

```python
from chatter_sdk.models.tool_server_health_check import ToolServerHealthCheck

# TODO update the JSON string below
json = "{}"
# create an instance of ToolServerHealthCheck from a JSON string
tool_server_health_check_instance = ToolServerHealthCheck.from_json(json)
# print the JSON string representation of the object
print(ToolServerHealthCheck.to_json())

# convert the object into a dict
tool_server_health_check_dict = tool_server_health_check_instance.to_dict()
# create an instance of ToolServerHealthCheck from a dict
tool_server_health_check_from_dict = ToolServerHealthCheck.from_dict(tool_server_health_check_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


