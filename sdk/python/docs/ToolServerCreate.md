# ToolServerCreate

Schema for creating a tool server.

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

## Example

```python
from chatter_sdk.models.tool_server_create import ToolServerCreate

# TODO update the JSON string below
json = "{}"
# create an instance of ToolServerCreate from a JSON string
tool_server_create_instance = ToolServerCreate.from_json(json)
# print the JSON string representation of the object
print(ToolServerCreate.to_json())

# convert the object into a dict
tool_server_create_dict = tool_server_create_instance.to_dict()
# create an instance of ToolServerCreate from a dict
tool_server_create_from_dict = ToolServerCreate.from_dict(tool_server_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


