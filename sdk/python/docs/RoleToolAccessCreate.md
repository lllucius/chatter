# RoleToolAccessCreate

Schema for creating role-based tool access.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**role** | [**UserRole**](UserRole.md) |  | 
**tool_pattern** | **str** |  | [optional] 
**server_pattern** | **str** |  | [optional] 
**access_level** | [**ToolAccessLevel**](ToolAccessLevel.md) |  | 
**default_rate_limit_per_hour** | **int** |  | [optional] 
**default_rate_limit_per_day** | **int** |  | [optional] 
**allowed_hours** | **List[int]** |  | [optional] 
**allowed_days** | **List[int]** |  | [optional] 

## Example

```python
from chatter_sdk.models.role_tool_access_create import RoleToolAccessCreate

# TODO update the JSON string below
json = "{}"
# create an instance of RoleToolAccessCreate from a JSON string
role_tool_access_create_instance = RoleToolAccessCreate.from_json(json)
# print the JSON string representation of the object
print(RoleToolAccessCreate.to_json())

# convert the object into a dict
role_tool_access_create_dict = role_tool_access_create_instance.to_dict()
# create an instance of RoleToolAccessCreate from a dict
role_tool_access_create_from_dict = RoleToolAccessCreate.from_dict(role_tool_access_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


