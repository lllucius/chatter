# ProfileUpdate

Schema for updating a profile.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**profile_type** | [**ProfileType**](ProfileType.md) |  | [optional] [default to undefined]
**llm_provider** | **string** |  | [optional] [default to undefined]
**llm_model** | **string** |  | [optional] [default to undefined]
**temperature** | **number** |  | [optional] [default to undefined]
**top_p** | **number** |  | [optional] [default to undefined]
**top_k** | **number** |  | [optional] [default to undefined]
**max_tokens** | **number** |  | [optional] [default to undefined]
**presence_penalty** | **number** |  | [optional] [default to undefined]
**frequency_penalty** | **number** |  | [optional] [default to undefined]
**context_window** | **number** |  | [optional] [default to undefined]
**system_prompt** | **string** |  | [optional] [default to undefined]
**memory_enabled** | **boolean** |  | [optional] [default to undefined]
**memory_strategy** | **string** |  | [optional] [default to undefined]
**enable_retrieval** | **boolean** |  | [optional] [default to undefined]
**retrieval_limit** | **number** |  | [optional] [default to undefined]
**retrieval_score_threshold** | **number** |  | [optional] [default to undefined]
**enable_tools** | **boolean** |  | [optional] [default to undefined]
**available_tools** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**tool_choice** | **string** |  | [optional] [default to undefined]
**content_filter_enabled** | **boolean** |  | [optional] [default to undefined]
**safety_level** | **string** |  | [optional] [default to undefined]
**response_format** | **string** |  | [optional] [default to undefined]
**stream_response** | **boolean** |  | [optional] [default to undefined]
**seed** | **number** |  | [optional] [default to undefined]
**stop_sequences** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**logit_bias** | **{ [key: string]: number; }** |  | [optional] [default to undefined]
**embedding_provider** | **string** |  | [optional] [default to undefined]
**embedding_model** | **string** |  | [optional] [default to undefined]
**is_public** | **boolean** |  | [optional] [default to undefined]
**tags** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**extra_metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { ProfileUpdate } from 'chatter-sdk';

const instance: ProfileUpdate = {
    name,
    description,
    profile_type,
    llm_provider,
    llm_model,
    temperature,
    top_p,
    top_k,
    max_tokens,
    presence_penalty,
    frequency_penalty,
    context_window,
    system_prompt,
    memory_enabled,
    memory_strategy,
    enable_retrieval,
    retrieval_limit,
    retrieval_score_threshold,
    enable_tools,
    available_tools,
    tool_choice,
    content_filter_enabled,
    safety_level,
    response_format,
    stream_response,
    seed,
    stop_sequences,
    logit_bias,
    embedding_provider,
    embedding_model,
    is_public,
    tags,
    extra_metadata,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
