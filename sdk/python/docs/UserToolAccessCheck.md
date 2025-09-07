# UserToolAccessCheck

Schema for checking user tool access.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**user_id** | **str** | User ID | 
**tool_name** | **str** | Tool name | 
**server_name** | **str** |  | [optional] 

## Example

```python
from chatter_sdk.models.user_tool_access_check import UserToolAccessCheck

# TODO update the JSON string below
json = "{}"
# create an instance of UserToolAccessCheck from a JSON string
user_tool_access_check_instance = UserToolAccessCheck.from_json(json)
# print the JSON string representation of the object
print(UserToolAccessCheck.to_json())

# convert the object into a dict
user_tool_access_check_dict = user_tool_access_check_instance.to_dict()
# create an instance of UserToolAccessCheck from a dict
user_tool_access_check_from_dict = UserToolAccessCheck.from_dict(user_tool_access_check_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


