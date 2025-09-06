# ModelDefCreate

Schema for creating a model definition.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Model name | 
**model_type** | [**ModelType**](ModelType.md) |  | 
**display_name** | **str** | Human-readable name | 
**description** | **str** |  | [optional] 
**model_name** | **str** | Actual model name for API calls | 
**max_tokens** | **int** |  | [optional] 
**context_length** | **int** |  | [optional] 
**dimensions** | **int** |  | [optional] 
**chunk_size** | **int** |  | [optional] 
**supports_batch** | **bool** | Whether model supports batch operations | [optional] [default to False]
**max_batch_size** | **int** |  | [optional] 
**default_config** | **Dict[str, object]** | Default configuration | [optional] 
**is_active** | **bool** | Whether model is active | [optional] [default to True]
**is_default** | **bool** | Whether this is the default model | [optional] [default to False]
**provider_id** | **str** | Provider ID | 

## Example

```python
from chatter_sdk.models.model_def_create import ModelDefCreate

# TODO update the JSON string below
json = "{}"
# create an instance of ModelDefCreate from a JSON string
model_def_create_instance = ModelDefCreate.from_json(json)
# print the JSON string representation of the object
print(ModelDefCreate.to_json())

# convert the object into a dict
model_def_create_dict = model_def_create_instance.to_dict()
# create an instance of ModelDefCreate from a dict
model_def_create_from_dict = ModelDefCreate.from_dict(model_def_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


