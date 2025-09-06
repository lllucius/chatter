# APIKeyCreate

Schema for API key creation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | API key name | 

## Example

```python
from chatter_sdk.models.api_key_create import APIKeyCreate

# TODO update the JSON string below
json = "{}"
# create an instance of APIKeyCreate from a JSON string
api_key_create_instance = APIKeyCreate.from_json(json)
# print the JSON string representation of the object
print(APIKeyCreate.to_json())

# convert the object into a dict
api_key_create_dict = api_key_create_instance.to_dict()
# create an instance of APIKeyCreate from a dict
api_key_create_from_dict = APIKeyCreate.from_dict(api_key_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


