# ProviderDefaultResponse

Response schema for setting default provider.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Operation result message | 

## Example

```python
from chatter_sdk.models.provider_default_response import ProviderDefaultResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ProviderDefaultResponse from a JSON string
provider_default_response_instance = ProviderDefaultResponse.from_json(json)
# print the JSON string representation of the object
print(ProviderDefaultResponse.to_json())

# convert the object into a dict
provider_default_response_dict = provider_default_response_instance.to_dict()
# create an instance of ProviderDefaultResponse from a dict
provider_default_response_from_dict = ProviderDefaultResponse.from_dict(provider_default_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


