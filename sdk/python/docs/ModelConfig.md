# ModelConfig

Model configuration for chat workflows.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**provider** | **str** |  | [optional] 
**model** | **str** |  | [optional] 
**temperature** | **float** | Temperature | [optional] [default to 0.7]
**max_tokens** | **int** | Max tokens | [optional] [default to 1000]
**top_p** | **float** | Top-p sampling | [optional] [default to 1.0]
**presence_penalty** | **float** | Presence penalty | [optional] [default to 0.0]
**frequency_penalty** | **float** | Frequency penalty | [optional] [default to 0.0]

## Example

```python
from chatter_sdk.models.model_config import ModelConfig

# TODO update the JSON string below
json = "{}"
# create an instance of ModelConfig from a JSON string
model_config_instance = ModelConfig.from_json(json)
# print the JSON string representation of the object
print(ModelConfig.to_json())

# convert the object into a dict
model_config_dict = model_config_instance.to_dict()
# create an instance of ModelConfig from a dict
model_config_from_dict = ModelConfig.from_dict(model_config_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


