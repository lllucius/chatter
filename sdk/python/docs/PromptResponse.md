# PromptResponse

Schema for prompt response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Prompt ID | 
**owner_id** | **str** | Owner user ID | 
**name** | **str** | Prompt name | 
**description** | **str** |  | [optional] 
**prompt_type** | [**PromptType**](PromptType.md) |  | 
**category** | [**PromptCategory**](PromptCategory.md) |  | 
**content** | **str** | Prompt content/template | 
**variables** | **List[str]** |  | [optional] 
**template_format** | **str** | Template format | 
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
**is_chain** | **bool** | Whether this is a chain prompt | 
**chain_steps** | **List[Dict[str, object]]** |  | [optional] 
**parent_prompt_id** | **str** |  | [optional] 
**version** | **int** | Prompt version | 
**is_latest** | **bool** | Whether this is the latest version | 
**changelog** | **str** |  | [optional] 
**is_public** | **bool** | Whether prompt is public | 
**rating** | **float** |  | [optional] 
**rating_count** | **int** | Number of ratings | 
**usage_count** | **int** | Usage count | 
**success_rate** | **float** |  | [optional] 
**avg_response_time_ms** | **int** |  | [optional] 
**last_used_at** | **datetime** |  | [optional] 
**total_tokens_used** | **int** | Total tokens used | 
**total_cost** | **float** | Total cost | 
**avg_tokens_per_use** | **float** |  | [optional] 
**tags** | **List[str]** |  | [optional] 
**extra_metadata** | **Dict[str, object]** |  | [optional] 
**content_hash** | **str** | Content hash | 
**estimated_tokens** | **int** |  | [optional] 
**language** | **str** |  | [optional] 
**created_at** | **datetime** | Creation timestamp | 
**updated_at** | **datetime** | Last update timestamp | 

## Example

```python
from chatter_sdk.models.prompt_response import PromptResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PromptResponse from a JSON string
prompt_response_instance = PromptResponse.from_json(json)
# print the JSON string representation of the object
print(PromptResponse.to_json())

# convert the object into a dict
prompt_response_dict = prompt_response_instance.to_dict()
# create an instance of PromptResponse from a dict
prompt_response_from_dict = PromptResponse.from_dict(prompt_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


