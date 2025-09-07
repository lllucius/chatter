# UserCreate

Schema for user creation (alias for UserRegistration).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **str** | User email address | 
**username** | **str** | Username | 
**full_name** | **str** |  | [optional] 
**bio** | **str** |  | [optional] 
**avatar_url** | **str** |  | [optional] 
**phone_number** | **str** |  | [optional] 
**password** | **str** | Password | 

## Example

```python
from chatter_sdk.models.user_create import UserCreate

# TODO update the JSON string below
json = "{}"
# create an instance of UserCreate from a JSON string
user_create_instance = UserCreate.from_json(json)
# print the JSON string representation of the object
print(UserCreate.to_json())

# convert the object into a dict
user_create_dict = user_create_instance.to_dict()
# create an instance of UserCreate from a dict
user_create_from_dict = UserCreate.from_dict(user_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


