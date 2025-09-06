# ModelDefWithProvider

Model definition with provider information.

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
**id** | **str** |  | 
**provider_id** | **str** |  | 
**created_at** | **datetime** |  | 
**updated_at** | **datetime** |  | 
**provider** | [**Provider**](Provider.md) |  | 

## Example

```python
from chatter_sdk.models.model_def_with_provider import ModelDefWithProvider

# TODO update the JSON string below
json = "{}"
# create an instance of ModelDefWithProvider from a JSON string
model_def_with_provider_instance = ModelDefWithProvider.from_json(json)
# print the JSON string representation of the object
print(ModelDefWithProvider.to_json())

# convert the object into a dict
model_def_with_provider_dict = model_def_with_provider_instance.to_dict()
# create an instance of ModelDefWithProvider from a dict
model_def_with_provider_from_dict = ModelDefWithProvider.from_dict(model_def_with_provider_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


