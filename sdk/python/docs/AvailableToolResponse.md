# AvailableToolResponse

Schema for individual available tool.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Tool name | 
**description** | **str** | Tool description | 
**type** | **str** | Tool type (mcp, builtin) | 
**args_schema** | **Dict[str, object]** | Tool arguments schema | 

## Example

```python
from chatter_sdk.models.available_tool_response import AvailableToolResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AvailableToolResponse from a JSON string
available_tool_response_instance = AvailableToolResponse.from_json(json)
# print the JSON string representation of the object
print(AvailableToolResponse.to_json())

# convert the object into a dict
available_tool_response_dict = available_tool_response_instance.to_dict()
# create an instance of AvailableToolResponse from a dict
available_tool_response_from_dict = AvailableToolResponse.from_dict(available_tool_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


