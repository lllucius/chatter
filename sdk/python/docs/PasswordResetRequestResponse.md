# PasswordResetRequestResponse

Schema for password reset request response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Success message | 

## Example

```python
from chatter_sdk.models.password_reset_request_response import PasswordResetRequestResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PasswordResetRequestResponse from a JSON string
password_reset_request_response_instance = PasswordResetRequestResponse.from_json(json)
# print the JSON string representation of the object
print(PasswordResetRequestResponse.to_json())

# convert the object into a dict
password_reset_request_response_dict = password_reset_request_response_instance.to_dict()
# create an instance of PasswordResetRequestResponse from a dict
password_reset_request_response_from_dict = PasswordResetRequestResponse.from_dict(password_reset_request_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


