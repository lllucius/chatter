# ServerToolResponse

Schema for server tool response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Tool name | 
**display_name** | **str** | Display name | 
**description** | **str** |  | [optional] 
**args_schema** | **Dict[str, object]** |  | [optional] 
**bypass_when_unavailable** | **bool** | Bypass when tool is unavailable | [optional] [default to False]
**id** | **str** | Tool ID | 
**server_id** | **str** | Server ID | 
**status** | [**ToolStatus**](ToolStatus.md) |  | 
**is_available** | **bool** | Tool availability | 
**total_calls** | **int** | Total number of calls | 
**total_errors** | **int** | Total number of errors | 
**last_called** | **datetime** |  | [optional] 
**last_error** | **str** |  | [optional] 
**avg_response_time_ms** | **float** |  | [optional] 
**created_at** | **datetime** | Creation timestamp | 
**updated_at** | **datetime** | Last update timestamp | 

## Example

```python
from chatter_sdk.models.server_tool_response import ServerToolResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ServerToolResponse from a JSON string
server_tool_response_instance = ServerToolResponse.from_json(json)
# print the JSON string representation of the object
print(ServerToolResponse.to_json())

# convert the object into a dict
server_tool_response_dict = server_tool_response_instance.to_dict()
# create an instance of ServerToolResponse from a dict
server_tool_response_from_dict = ServerToolResponse.from_dict(server_tool_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


