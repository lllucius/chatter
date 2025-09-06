# PromptCreate

Schema for creating a prompt.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Prompt name | 
**description** | **str** |  | [optional] 
**prompt_type** | [**PromptType**](PromptType.md) |  | [optional] 
**category** | [**PromptCategory**](PromptCategory.md) |  | [optional] 
**content** | **str** | Prompt content/template | 
**variables** | **List[str]** |  | [optional] 
**template_format** | **str** | Template format (f-string, jinja2, mustache) | [optional] [default to 'f-string']
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
**is_chain** | **bool** | Whether this is a chain prompt | [optional] [default to False]
**chain_steps** | **List[Dict[str, object]]** |  | [optional] 
**parent_prompt_id** | **str** |  | [optional] 
**is_public** | **bool** | Whether prompt is public | [optional] [default to False]
**tags** | **List[str]** |  | [optional] 
**extra_metadata** | **Dict[str, object]** |  | [optional] 

## Example

```python
from chatter_sdk.models.prompt_create import PromptCreate

# TODO update the JSON string below
json = "{}"
# create an instance of PromptCreate from a JSON string
prompt_create_instance = PromptCreate.from_json(json)
# print the JSON string representation of the object
print(PromptCreate.to_json())

# convert the object into a dict
prompt_create_dict = prompt_create_instance.to_dict()
# create an instance of PromptCreate from a dict
prompt_create_from_dict = PromptCreate.from_dict(prompt_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


