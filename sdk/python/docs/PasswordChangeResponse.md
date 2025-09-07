# PasswordChangeResponse

Schema for password change response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Success message | 

## Example

```python
from chatter_sdk.models.password_change_response import PasswordChangeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PasswordChangeResponse from a JSON string
password_change_response_instance = PasswordChangeResponse.from_json(json)
# print the JSON string representation of the object
print(PasswordChangeResponse.to_json())

# convert the object into a dict
password_change_response_dict = password_change_response_instance.to_dict()
# create an instance of PasswordChangeResponse from a dict
password_change_response_from_dict = PasswordChangeResponse.from_dict(password_change_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


