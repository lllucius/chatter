# PasswordChange

Schema for password change.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**current_password** | **str** | Current password | 
**new_password** | **str** | New password | 

## Example

```python
from chatter_sdk.models.password_change import PasswordChange

# TODO update the JSON string below
json = "{}"
# create an instance of PasswordChange from a JSON string
password_change_instance = PasswordChange.from_json(json)
# print the JSON string representation of the object
print(PasswordChange.to_json())

# convert the object into a dict
password_change_dict = password_change_instance.to_dict()
# create an instance of PasswordChange from a dict
password_change_from_dict = PasswordChange.from_dict(password_change_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


