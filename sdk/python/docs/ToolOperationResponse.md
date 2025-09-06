# ToolOperationResponse

Schema for tool operation response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Operation success status | 
**message** | **str** | Operation result message | 

## Example

```python
from chatter_sdk.models.tool_operation_response import ToolOperationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ToolOperationResponse from a JSON string
tool_operation_response_instance = ToolOperationResponse.from_json(json)
# print the JSON string representation of the object
print(ToolOperationResponse.to_json())

# convert the object into a dict
tool_operation_response_dict = tool_operation_response_instance.to_dict()
# create an instance of ToolOperationResponse from a dict
tool_operation_response_from_dict = ToolOperationResponse.from_dict(tool_operation_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


