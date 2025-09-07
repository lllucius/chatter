# AvailableProvidersResponse

Schema for available providers response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**providers** | **Dict[str, object]** | Available LLM providers with their configurations | 
**total_providers** | **int** | Total number of available providers | 
**supported_features** | **Dict[str, List[str]]** | Features supported by each provider | 

## Example

```python
from chatter_sdk.models.available_providers_response import AvailableProvidersResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AvailableProvidersResponse from a JSON string
available_providers_response_instance = AvailableProvidersResponse.from_json(json)
# print the JSON string representation of the object
print(AvailableProvidersResponse.to_json())

# convert the object into a dict
available_providers_response_dict = available_providers_response_instance.to_dict()
# create an instance of AvailableProvidersResponse from a dict
available_providers_response_from_dict = AvailableProvidersResponse.from_dict(available_providers_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


