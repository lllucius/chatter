# ProviderUpdate

Schema for updating a provider.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**display_name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**api_key_required** | **bool** |  | [optional] 
**base_url** | **str** |  | [optional] 
**default_config** | **Dict[str, object]** |  | [optional] 
**is_active** | **bool** |  | [optional] 
**is_default** | **bool** |  | [optional] 

## Example

```python
from chatter_sdk.models.provider_update import ProviderUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of ProviderUpdate from a JSON string
provider_update_instance = ProviderUpdate.from_json(json)
# print the JSON string representation of the object
print(ProviderUpdate.to_json())

# convert the object into a dict
provider_update_dict = provider_update_instance.to_dict()
# create an instance of ProviderUpdate from a dict
provider_update_from_dict = ProviderUpdate.from_dict(provider_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


