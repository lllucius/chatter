# ProviderDeleteResponse

Response schema for provider deletion.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Deletion result message | 

## Example

```python
from chatter_sdk.models.provider_delete_response import ProviderDeleteResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ProviderDeleteResponse from a JSON string
provider_delete_response_instance = ProviderDeleteResponse.from_json(json)
# print the JSON string representation of the object
print(ProviderDeleteResponse.to_json())

# convert the object into a dict
provider_delete_response_dict = provider_delete_response_instance.to_dict()
# create an instance of ProviderDeleteResponse from a dict
provider_delete_response_from_dict = ProviderDeleteResponse.from_dict(provider_delete_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


