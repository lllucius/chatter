# Provider

Full provider schema.

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
**id** | **str** |  | 
**created_at** | **datetime** |  | 
**updated_at** | **datetime** |  | 

## Example

```python
from chatter_sdk.models.provider import Provider

# TODO update the JSON string below
json = "{}"
# create an instance of Provider from a JSON string
provider_instance = Provider.from_json(json)
# print the JSON string representation of the object
print(Provider.to_json())

# convert the object into a dict
provider_dict = provider_instance.to_dict()
# create an instance of Provider from a dict
provider_from_dict = Provider.from_dict(provider_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


