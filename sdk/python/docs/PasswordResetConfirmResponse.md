# PasswordResetConfirmResponse

Schema for password reset confirmation response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Success message | 

## Example

```python
from chatter_sdk.models.password_reset_confirm_response import PasswordResetConfirmResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PasswordResetConfirmResponse from a JSON string
password_reset_confirm_response_instance = PasswordResetConfirmResponse.from_json(json)
# print the JSON string representation of the object
print(PasswordResetConfirmResponse.to_json())

# convert the object into a dict
password_reset_confirm_response_dict = password_reset_confirm_response_instance.to_dict()
# create an instance of PasswordResetConfirmResponse from a dict
password_reset_confirm_response_from_dict = PasswordResetConfirmResponse.from_dict(password_reset_confirm_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


