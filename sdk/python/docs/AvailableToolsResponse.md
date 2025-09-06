# AvailableToolsResponse

Schema for available tools response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tools** | [**List[AvailableToolResponse]**](AvailableToolResponse.md) | Available tools | 

## Example

```python
from chatter_sdk.models.available_tools_response import AvailableToolsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AvailableToolsResponse from a JSON string
available_tools_response_instance = AvailableToolsResponse.from_json(json)
# print the JSON string representation of the object
print(AvailableToolsResponse.to_json())

# convert the object into a dict
available_tools_response_dict = available_tools_response_instance.to_dict()
# create an instance of AvailableToolsResponse from a dict
available_tools_response_from_dict = AvailableToolsResponse.from_dict(available_tools_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


