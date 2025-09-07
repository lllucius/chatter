# ToolServerDeleteResponse

Schema for tool server delete response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Success message | 

## Example

```python
from chatter_sdk.models.tool_server_delete_response import ToolServerDeleteResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ToolServerDeleteResponse from a JSON string
tool_server_delete_response_instance = ToolServerDeleteResponse.from_json(json)
# print the JSON string representation of the object
print(ToolServerDeleteResponse.to_json())

# convert the object into a dict
tool_server_delete_response_dict = tool_server_delete_response_instance.to_dict()
# create an instance of ToolServerDeleteResponse from a dict
tool_server_delete_response_from_dict = ToolServerDeleteResponse.from_dict(tool_server_delete_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


