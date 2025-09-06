# PromptUpdate

Schema for updating a prompt.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**prompt_type** | [**PromptType**](PromptType.md) |  | [optional] 
**category** | [**PromptCategory**](PromptCategory.md) |  | [optional] 
**content** | **str** |  | [optional] 
**variables** | **List[str]** |  | [optional] 
**template_format** | **str** |  | [optional] 
**input_schema** | **Dict[str, object]** |  | [optional] 
**output_schema** | **Dict[str, object]** |  | [optional] 
**max_length** | **int** |  | [optional] 
**min_length** | **int** |  | [optional] 
**required_variables** | **List[str]** |  | [optional] 
**examples** | **List[Dict[str, object]]** |  | [optional] 
**test_cases** | **List[Dict[str, object]]** |  | [optional] 
**suggested_temperature** | **float** |  | [optional] 
**suggested_max_tokens** | **int** |  | [optional] 
**suggested_providers** | **List[str]** |  | [optional] 
**is_chain** | **bool** |  | [optional] 
**chain_steps** | **List[Dict[str, object]]** |  | [optional] 
**parent_prompt_id** | **str** |  | [optional] 
**is_public** | **bool** |  | [optional] 
**tags** | **List[str]** |  | [optional] 
**extra_metadata** | **Dict[str, object]** |  | [optional] 

## Example

```python
from chatter_sdk.models.prompt_update import PromptUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of PromptUpdate from a JSON string
prompt_update_instance = PromptUpdate.from_json(json)
# print the JSON string representation of the object
print(PromptUpdate.to_json())

# convert the object into a dict
prompt_update_dict = prompt_update_instance.to_dict()
# create an instance of PromptUpdate from a dict
prompt_update_from_dict = PromptUpdate.from_dict(prompt_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


