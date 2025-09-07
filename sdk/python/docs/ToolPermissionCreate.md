# ToolPermissionCreate

Schema for creating tool permissions.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | User ID | 
**tool_id** | **str** |  | [optional] 
**server_id** | **str** |  | [optional] 
**access_level** | [**ToolAccessLevel**](ToolAccessLevel.md) |  | 
**rate_limit_per_hour** | **int** |  | [optional] 
**rate_limit_per_day** | **int** |  | [optional] 
**allowed_hours** | **List[int]** |  | [optional] 
**allowed_days** | **List[int]** |  | [optional] 
**expires_at** | **datetime** |  | [optional] 

## Example

```python
from chatter_sdk.models.tool_permission_create import ToolPermissionCreate

# TODO update the JSON string below
json = "{}"
# create an instance of ToolPermissionCreate from a JSON string
tool_permission_create_instance = ToolPermissionCreate.from_json(json)
# print the JSON string representation of the object
print(ToolPermissionCreate.to_json())

# convert the object into a dict
tool_permission_create_dict = tool_permission_create_instance.to_dict()
# create an instance of ToolPermissionCreate from a dict
tool_permission_create_from_dict = ToolPermissionCreate.from_dict(tool_permission_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


