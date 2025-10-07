# ProviderList

List of providers with pagination.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**providers** | [**List[Provider]**](Provider.md) |  | 
**total** | **int** |  | 
**limit** | **int** |  | 
**offset** | **int** |  | 

## Example

```python
from chatter_sdk.models.provider_list import ProviderList

# TODO update the JSON string below
json = "{}"
# create an instance of ProviderList from a JSON string
provider_list_instance = ProviderList.from_json(json)
# print the JSON string representation of the object
print(ProviderList.to_json())

# convert the object into a dict
provider_list_dict = provider_list_instance.to_dict()
# create an instance of ProviderList from a dict
provider_list_from_dict = ProviderList.from_dict(provider_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


