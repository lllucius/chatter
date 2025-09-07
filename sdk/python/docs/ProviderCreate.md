# ProviderCreate

Schema for creating a provider.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Unique provider name | 
**provider_type** | [**ProviderType**](ProviderType.md) |  | 
**display_name** | **str** | Human-readable name | 
**description** | **str** |  | [optional] 
**api_key_required** | **bool** | Whether API key is required | [optional] [default to True]
**base_url** | **str** |  | [optional] 
**default_config** | **Dict[str, object]** | Default configuration | [optional] 
**is_active** | **bool** | Whether provider is active | [optional] [default to True]
**is_default** | **bool** | Whether this is the default provider | [optional] [default to False]

## Example

```python
from chatter_sdk.models.provider_create import ProviderCreate

# TODO update the JSON string below
json = "{}"
# create an instance of ProviderCreate from a JSON string
provider_create_instance = ProviderCreate.from_json(json)
# print the JSON string representation of the object
print(ProviderCreate.to_json())

# convert the object into a dict
provider_create_dict = provider_create_instance.to_dict()
# create an instance of ProviderCreate from a dict
provider_create_from_dict = ProviderCreate.from_dict(provider_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


