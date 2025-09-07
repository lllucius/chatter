# ToolServerResponse

Schema for tool server response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Server name | 
**display_name** | **str** | Display name | 
**description** | **str** |  | [optional] 
**base_url** | **str** |  | [optional] 
**transport_type** | **str** | Transport type: http, sse, stdio, or websocket | [optional] [default to 'http']
**oauth_config** | [**OAuthConfigSchema**](OAuthConfigSchema.md) |  | [optional] 
**headers** | **Dict[str, str]** |  | [optional] 
**timeout** | **int** | Request timeout in seconds | [optional] [default to 30]
**auto_start** | **bool** | Auto-connect to server on system startup | [optional] [default to True]
**auto_update** | **bool** | Auto-update server capabilities | [optional] [default to True]
**max_failures** | **int** | Maximum consecutive failures before disabling | [optional] [default to 3]
**id** | **str** | Server ID | 
**status** | [**ServerStatus**](ServerStatus.md) |  | 
**is_builtin** | **bool** | Whether server is built-in | 
**last_health_check** | **datetime** |  | [optional] 
**last_startup_success** | **datetime** |  | [optional] 
**last_startup_error** | **str** |  | [optional] 
**consecutive_failures** | **int** | Consecutive failure count | 
**created_at** | **datetime** | Creation timestamp | 
**updated_at** | **datetime** | Last update timestamp | 
**created_by** | **str** |  | [optional] 
**tools** | [**List[ServerToolResponse]**](ServerToolResponse.md) | Server tools | [optional] 

## Example

```python
from chatter_sdk.models.tool_server_response import ToolServerResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ToolServerResponse from a JSON string
tool_server_response_instance = ToolServerResponse.from_json(json)
# print the JSON string representation of the object
print(ToolServerResponse.to_json())

# convert the object into a dict
tool_server_response_dict = tool_server_response_instance.to_dict()
# create an instance of ToolServerResponse from a dict
tool_server_response_from_dict = ToolServerResponse.from_dict(tool_server_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


