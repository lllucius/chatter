# RoleToolAccessResponse

Schema for role-based tool access response.

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
**id** | **str** | Access rule ID | 
**created_by** | **str** | Creator user ID | 
**created_at** | **datetime** | Creation timestamp | 

## Example

```python
from chatter_sdk.models.role_tool_access_response import RoleToolAccessResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RoleToolAccessResponse from a JSON string
role_tool_access_response_instance = RoleToolAccessResponse.from_json(json)
# print the JSON string representation of the object
print(RoleToolAccessResponse.to_json())

# convert the object into a dict
role_tool_access_response_dict = role_tool_access_response_instance.to_dict()
# create an instance of RoleToolAccessResponse from a dict
role_tool_access_response_from_dict = RoleToolAccessResponse.from_dict(role_tool_access_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


