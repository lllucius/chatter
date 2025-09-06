# PromptStatsResponse

Schema for prompt statistics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_prompts** | **int** | Total number of prompts | 
**prompts_by_type** | **Dict[str, int]** | Prompts by type | 
**prompts_by_category** | **Dict[str, int]** | Prompts by category | 
**most_used_prompts** | [**List[PromptResponse]**](PromptResponse.md) | Most used prompts | 
**recent_prompts** | [**List[PromptResponse]**](PromptResponse.md) | Recently created prompts | 
**usage_stats** | **Dict[str, object]** | Usage statistics | 

## Example

```python
from chatter_sdk.models.prompt_stats_response import PromptStatsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PromptStatsResponse from a JSON string
prompt_stats_response_instance = PromptStatsResponse.from_json(json)
# print the JSON string representation of the object
print(PromptStatsResponse.to_json())

# convert the object into a dict
prompt_stats_response_dict = prompt_stats_response_instance.to_dict()
# create an instance of PromptStatsResponse from a dict
prompt_stats_response_from_dict = PromptStatsResponse.from_dict(prompt_stats_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


