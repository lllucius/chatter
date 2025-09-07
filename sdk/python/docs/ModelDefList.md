# ModelDefList

List of model definitions with pagination.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**models** | [**List[ModelDefWithProvider]**](ModelDefWithProvider.md) |  | 
**total** | **int** |  | 
**page** | **int** |  | 
**per_page** | **int** |  | 

## Example

```python
from chatter_sdk.models.model_def_list import ModelDefList

# TODO update the JSON string below
json = "{}"
# create an instance of ModelDefList from a JSON string
model_def_list_instance = ModelDefList.from_json(json)
# print the JSON string representation of the object
print(ModelDefList.to_json())

# convert the object into a dict
model_def_list_dict = model_def_list_instance.to_dict()
# create an instance of ModelDefList from a dict
model_def_list_from_dict = ModelDefList.from_dict(model_def_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


