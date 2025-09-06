# ToolPermissionUpdate

Schema for updating tool permissions.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**access_level** | [**ToolAccessLevel**](ToolAccessLevel.md) |  | [optional] 
**rate_limit_per_hour** | **int** |  | [optional] 
**rate_limit_per_day** | **int** |  | [optional] 
**allowed_hours** | **List[int]** |  | [optional] 
**allowed_days** | **List[int]** |  | [optional] 
**expires_at** | **datetime** |  | [optional] 

## Example

```python
from chatter_sdk.models.tool_permission_update import ToolPermissionUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of ToolPermissionUpdate from a JSON string
tool_permission_update_instance = ToolPermissionUpdate.from_json(json)
# print the JSON string representation of the object
print(ToolPermissionUpdate.to_json())

# convert the object into a dict
tool_permission_update_dict = tool_permission_update_instance.to_dict()
# create an instance of ToolPermissionUpdate from a dict
tool_permission_update_from_dict = ToolPermissionUpdate.from_dict(tool_permission_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


