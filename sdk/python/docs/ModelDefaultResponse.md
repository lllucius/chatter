# ModelDefaultResponse

Response schema for setting default model.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Operation result message | 

## Example

```python
from chatter_sdk.models.model_default_response import ModelDefaultResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ModelDefaultResponse from a JSON string
model_default_response_instance = ModelDefaultResponse.from_json(json)
# print the JSON string representation of the object
print(ModelDefaultResponse.to_json())

# convert the object into a dict
model_default_response_dict = model_default_response_instance.to_dict()
# create an instance of ModelDefaultResponse from a dict
model_default_response_from_dict = ModelDefaultResponse.from_dict(model_default_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


