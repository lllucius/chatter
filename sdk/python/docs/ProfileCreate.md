# ProfileCreate

Schema for creating a profile.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Profile name | 
**description** | **str** |  | [optional] 
**profile_type** | [**ProfileType**](ProfileType.md) |  | [optional] 
**llm_provider** | **str** | LLM provider (openai, anthropic, google, cohere, mistral, local, etc.) | 
**llm_model** | **str** | LLM model name | 
**temperature** | **float** | Temperature for generation | [optional] [default to 0.7]
**top_p** | **float** |  | [optional] 
**top_k** | **int** |  | [optional] 
**max_tokens** | **int** | Maximum tokens to generate | [optional] [default to 4096]
**presence_penalty** | **float** |  | [optional] 
**frequency_penalty** | **float** |  | [optional] 
**context_window** | **int** | Context window size | [optional] [default to 4096]
**system_prompt** | **str** |  | [optional] 
**memory_enabled** | **bool** | Enable conversation memory | [optional] [default to True]
**memory_strategy** | **str** |  | [optional] 
**enable_retrieval** | **bool** | Enable document retrieval | [optional] [default to False]
**retrieval_limit** | **int** | Number of documents to retrieve | [optional] [default to 5]
**retrieval_score_threshold** | **float** | Minimum retrieval score | [optional] [default to 0.7]
**enable_tools** | **bool** | Enable tool calling | [optional] [default to False]
**available_tools** | **List[str]** |  | [optional] 
**tool_choice** | **str** |  | [optional] 
**content_filter_enabled** | **bool** | Enable content filtering | [optional] [default to True]
**safety_level** | **str** |  | [optional] 
**response_format** | **str** |  | [optional] 
**stream_response** | **bool** | Enable streaming responses | [optional] [default to True]
**seed** | **int** |  | [optional] 
**stop_sequences** | **List[str]** |  | [optional] 
**logit_bias** | **Dict[str, float]** |  | [optional] 
**embedding_provider** | **str** |  | [optional] 
**embedding_model** | **str** |  | [optional] 
**is_public** | **bool** | Whether profile is public | [optional] [default to False]
**tags** | **List[str]** |  | [optional] 
**extra_metadata** | **Dict[str, object]** |  | [optional] 

## Example

```python
from chatter_sdk.models.profile_create import ProfileCreate

# TODO update the JSON string below
json = "{}"
# create an instance of ProfileCreate from a JSON string
profile_create_instance = ProfileCreate.from_json(json)
# print the JSON string representation of the object
print(ProfileCreate.to_json())

# convert the object into a dict
profile_create_dict = profile_create_instance.to_dict()
# create an instance of ProfileCreate from a dict
profile_create_from_dict = ProfileCreate.from_dict(profile_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


