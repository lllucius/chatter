# ProfileUpdate

Schema for updating a profile.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**profile_type** | [**ProfileType**](ProfileType.md) |  | [optional] 
**llm_provider** | **str** |  | [optional] 
**llm_model** | **str** |  | [optional] 
**temperature** | **float** |  | [optional] 
**top_p** | **float** |  | [optional] 
**top_k** | **int** |  | [optional] 
**max_tokens** | **int** |  | [optional] 
**presence_penalty** | **float** |  | [optional] 
**frequency_penalty** | **float** |  | [optional] 
**context_window** | **int** |  | [optional] 
**system_prompt** | **str** |  | [optional] 
**memory_enabled** | **bool** |  | [optional] 
**memory_strategy** | **str** |  | [optional] 
**enable_retrieval** | **bool** |  | [optional] 
**retrieval_limit** | **int** |  | [optional] 
**retrieval_score_threshold** | **float** |  | [optional] 
**enable_tools** | **bool** |  | [optional] 
**available_tools** | **List[str]** |  | [optional] 
**tool_choice** | **str** |  | [optional] 
**content_filter_enabled** | **bool** |  | [optional] 
**safety_level** | **str** |  | [optional] 
**response_format** | **str** |  | [optional] 
**stream_response** | **bool** |  | [optional] 
**seed** | **int** |  | [optional] 
**stop_sequences** | **List[str]** |  | [optional] 
**logit_bias** | **Dict[str, float]** |  | [optional] 
**embedding_provider** | **str** |  | [optional] 
**embedding_model** | **str** |  | [optional] 
**is_public** | **bool** |  | [optional] 
**tags** | **List[str]** |  | [optional] 
**extra_metadata** | **Dict[str, object]** |  | [optional] 

## Example

```python
from chatter_sdk.models.profile_update import ProfileUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of ProfileUpdate from a JSON string
profile_update_instance = ProfileUpdate.from_json(json)
# print the JSON string representation of the object
print(ProfileUpdate.to_json())

# convert the object into a dict
profile_update_dict = profile_update_instance.to_dict()
# create an instance of ProfileUpdate from a dict
profile_update_from_dict = ProfileUpdate.from_dict(profile_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


