# ToolPermissionResponse

Schema for tool permission response.

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
**id** | **str** | Permission ID | 
**granted_by** | **str** | Granter user ID | 
**granted_at** | **datetime** | Grant timestamp | 
**usage_count** | **int** | Usage count | 
**last_used** | **datetime** |  | [optional] 

## Example

```python
from chatter_sdk.models.tool_permission_response import ToolPermissionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ToolPermissionResponse from a JSON string
tool_permission_response_instance = ToolPermissionResponse.from_json(json)
# print the JSON string representation of the object
print(ToolPermissionResponse.to_json())

# convert the object into a dict
tool_permission_response_dict = tool_permission_response_instance.to_dict()
# create an instance of ToolPermissionResponse from a dict
tool_permission_response_from_dict = ToolPermissionResponse.from_dict(tool_permission_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


