# DefaultProvider

Schema for setting default provider.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**model_type** | [**ModelType**](ModelType.md) |  | 

## Example

```python
from chatter_sdk.models.default_provider import DefaultProvider

# TODO update the JSON string below
json = "{}"
# create an instance of DefaultProvider from a JSON string
default_provider_instance = DefaultProvider.from_json(json)
# print the JSON string representation of the object
print(DefaultProvider.to_json())

# convert the object into a dict
default_provider_dict = default_provider_instance.to_dict()
# create an instance of DefaultProvider from a dict
default_provider_from_dict = DefaultProvider.from_dict(default_provider_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


