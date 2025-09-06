# ModelDefUpdate

Schema for updating a model definition.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**display_name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**model_name** | **str** |  | [optional] 
**max_tokens** | **int** |  | [optional] 
**context_length** | **int** |  | [optional] 
**dimensions** | **int** |  | [optional] 
**chunk_size** | **int** |  | [optional] 
**supports_batch** | **bool** |  | [optional] 
**max_batch_size** | **int** |  | [optional] 
**default_config** | **Dict[str, object]** |  | [optional] 
**is_active** | **bool** |  | [optional] 
**is_default** | **bool** |  | [optional] 

## Example

```python
from chatter_sdk.models.model_def_update import ModelDefUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of ModelDefUpdate from a JSON string
model_def_update_instance = ModelDefUpdate.from_json(json)
# print the JSON string representation of the object
print(ModelDefUpdate.to_json())

# convert the object into a dict
model_def_update_dict = model_def_update_instance.to_dict()
# create an instance of ModelDefUpdate from a dict
model_def_update_from_dict = ModelDefUpdate.from_dict(model_def_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


