# UserUpdate

Schema for user profile updates.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **str** |  | [optional] 
**full_name** | **str** |  | [optional] 
**bio** | **str** |  | [optional] 
**avatar_url** | **str** |  | [optional] 
**phone_number** | **str** |  | [optional] 
**default_llm_provider** | **str** |  | [optional] 
**default_profile_id** | **str** |  | [optional] 

## Example

```python
from chatter_sdk.models.user_update import UserUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of UserUpdate from a JSON string
user_update_instance = UserUpdate.from_json(json)
# print the JSON string representation of the object
print(UserUpdate.to_json())

# convert the object into a dict
user_update_dict = user_update_instance.to_dict()
# create an instance of UserUpdate from a dict
user_update_from_dict = UserUpdate.from_dict(user_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


