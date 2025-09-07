# APIKeyRevokeResponse

Schema for API key revoke response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Success message | 

## Example

```python
from chatter_sdk.models.api_key_revoke_response import APIKeyRevokeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of APIKeyRevokeResponse from a JSON string
api_key_revoke_response_instance = APIKeyRevokeResponse.from_json(json)
# print the JSON string representation of the object
print(APIKeyRevokeResponse.to_json())

# convert the object into a dict
api_key_revoke_response_dict = api_key_revoke_response_instance.to_dict()
# create an instance of APIKeyRevokeResponse from a dict
api_key_revoke_response_from_dict = APIKeyRevokeResponse.from_dict(api_key_revoke_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


