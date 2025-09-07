# ModelDeleteResponse

Response schema for model deletion.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Deletion result message | 

## Example

```python
from chatter_sdk.models.model_delete_response import ModelDeleteResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ModelDeleteResponse from a JSON string
model_delete_response_instance = ModelDeleteResponse.from_json(json)
# print the JSON string representation of the object
print(ModelDeleteResponse.to_json())

# convert the object into a dict
model_delete_response_dict = model_delete_response_instance.to_dict()
# create an instance of ModelDeleteResponse from a dict
model_delete_response_from_dict = ModelDeleteResponse.from_dict(model_delete_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


