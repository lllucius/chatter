# ToolServerOperationResponse

Schema for tool server operation response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Operation success status | 
**message** | **str** | Operation result message | 

## Example

```python
from chatter_sdk.models.tool_server_operation_response import ToolServerOperationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ToolServerOperationResponse from a JSON string
tool_server_operation_response_instance = ToolServerOperationResponse.from_json(json)
# print the JSON string representation of the object
print(ToolServerOperationResponse.to_json())

# convert the object into a dict
tool_server_operation_response_dict = tool_server_operation_response_instance.to_dict()
# create an instance of ToolServerOperationResponse from a dict
tool_server_operation_response_from_dict = ToolServerOperationResponse.from_dict(tool_server_operation_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


