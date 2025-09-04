# ProfileCreate

Schema for creating a profile.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | Profile name | [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**profile_type** | [**ProfileType**](ProfileType.md) | Profile type | [optional] [default to undefined]
**llm_provider** | **string** | LLM provider (openai, anthropic, etc.) | [default to undefined]
**llm_model** | **string** | LLM model name | [default to undefined]
**temperature** | **number** | Temperature for generation | [optional] [default to 0.7]
**top_p** | **number** |  | [optional] [default to undefined]
**top_k** | **number** |  | [optional] [default to undefined]
**max_tokens** | **number** | Maximum tokens to generate | [optional] [default to 4096]
**presence_penalty** | **number** |  | [optional] [default to undefined]
**frequency_penalty** | **number** |  | [optional] [default to undefined]
**context_window** | **number** | Context window size | [optional] [default to 4096]
**system_prompt** | **string** |  | [optional] [default to undefined]
**memory_enabled** | **boolean** | Enable conversation memory | [optional] [default to true]
**memory_strategy** | **string** |  | [optional] [default to undefined]
**enable_retrieval** | **boolean** | Enable document retrieval | [optional] [default to false]
**retrieval_limit** | **number** | Number of documents to retrieve | [optional] [default to 5]
**retrieval_score_threshold** | **number** | Minimum retrieval score | [optional] [default to 0.7]
**enable_tools** | **boolean** | Enable tool calling | [optional] [default to false]
**available_tools** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**tool_choice** | **string** |  | [optional] [default to undefined]
**content_filter_enabled** | **boolean** | Enable content filtering | [optional] [default to true]
**safety_level** | **string** |  | [optional] [default to undefined]
**response_format** | **string** |  | [optional] [default to undefined]
**stream_response** | **boolean** | Enable streaming responses | [optional] [default to true]
**seed** | **number** |  | [optional] [default to undefined]
**stop_sequences** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**logit_bias** | **{ [key: string]: number; }** |  | [optional] [default to undefined]
**embedding_provider** | **string** |  | [optional] [default to undefined]
**embedding_model** | **string** |  | [optional] [default to undefined]
**is_public** | **boolean** | Whether profile is public | [optional] [default to false]
**tags** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**extra_metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { ProfileCreate } from 'chatter-sdk';

const instance: ProfileCreate = {
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
