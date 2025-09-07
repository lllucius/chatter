# AccountDeactivateResponse

Schema for account deactivation response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Success message | 

## Example

```python
from chatter_sdk.models.account_deactivate_response import AccountDeactivateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AccountDeactivateResponse from a JSON string
account_deactivate_response_instance = AccountDeactivateResponse.from_json(json)
# print the JSON string representation of the object
print(AccountDeactivateResponse.to_json())

# convert the object into a dict
account_deactivate_response_dict = account_deactivate_response_instance.to_dict()
# create an instance of AccountDeactivateResponse from a dict
account_deactivate_response_from_dict = AccountDeactivateResponse.from_dict(account_deactivate_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


