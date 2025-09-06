# UserResponse

Schema for user response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**email** | **str** | User email address | 
**username** | **str** | Username | 
**full_name** | **str** |  | [optional] 
**bio** | **str** |  | [optional] 
**avatar_url** | **str** |  | [optional] 
**phone_number** | **str** |  | [optional] 
**id** | **str** | User ID | 
**is_active** | **bool** | Is user active | 
**is_verified** | **bool** | Is user email verified | 
**is_superuser** | **bool** | Is user a superuser | 
**default_llm_provider** | **str** |  | [optional] 
**default_profile_id** | **str** |  | [optional] 
**daily_message_limit** | **int** |  | [optional] 
**monthly_message_limit** | **int** |  | [optional] 
**max_file_size_mb** | **int** |  | [optional] 
**api_key_name** | **str** |  | [optional] 
**created_at** | **datetime** | Account creation date | 
**updated_at** | **datetime** | Last update date | 
**last_login_at** | **datetime** |  | [optional] 

## Example

```python
from chatter_sdk.models.user_response import UserResponse

# TODO update the JSON string below
json = "{}"
# create an instance of UserResponse from a JSON string
user_response_instance = UserResponse.from_json(json)
# print the JSON string representation of the object
print(UserResponse.to_json())

# convert the object into a dict
user_response_dict = user_response_instance.to_dict()
# create an instance of UserResponse from a dict
user_response_from_dict = UserResponse.from_dict(user_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


