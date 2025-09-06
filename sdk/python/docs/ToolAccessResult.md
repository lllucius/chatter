# ToolAccessResult

Schema for tool access check result.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**allowed** | **bool** | Whether access is allowed | 
**access_level** | [**ToolAccessLevel**](ToolAccessLevel.md) |  | 
**rate_limit_remaining_hour** | **int** |  | [optional] 
**rate_limit_remaining_day** | **int** |  | [optional] 
**restriction_reason** | **str** |  | [optional] 
**expires_at** | **datetime** |  | [optional] 

## Example

```python
from chatter_sdk.models.tool_access_result import ToolAccessResult

# TODO update the JSON string below
json = "{}"
# create an instance of ToolAccessResult from a JSON string
tool_access_result_instance = ToolAccessResult.from_json(json)
# print the JSON string representation of the object
print(ToolAccessResult.to_json())

# convert the object into a dict
tool_access_result_dict = tool_access_result_instance.to_dict()
# create an instance of ToolAccessResult from a dict
tool_access_result_from_dict = ToolAccessResult.from_dict(tool_access_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


