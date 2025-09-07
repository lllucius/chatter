# ToolServerUpdate

Schema for updating a remote tool server.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**display_name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**base_url** | **str** |  | [optional] 
**transport_type** | **str** |  | [optional] 
**oauth_config** | [**OAuthConfigSchema**](OAuthConfigSchema.md) |  | [optional] 
**headers** | **Dict[str, str]** |  | [optional] 
**timeout** | **int** |  | [optional] 
**auto_start** | **bool** |  | [optional] 
**auto_update** | **bool** |  | [optional] 
**max_failures** | **int** |  | [optional] 

## Example

```python
from chatter_sdk.models.tool_server_update import ToolServerUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of ToolServerUpdate from a JSON string
tool_server_update_instance = ToolServerUpdate.from_json(json)
# print the JSON string representation of the object
print(ToolServerUpdate.to_json())

# convert the object into a dict
tool_server_update_dict = tool_server_update_instance.to_dict()
# create an instance of ToolServerUpdate from a dict
tool_server_update_from_dict = ToolServerUpdate.from_dict(tool_server_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


