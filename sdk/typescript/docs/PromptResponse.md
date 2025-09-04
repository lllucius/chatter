# PromptResponse

Schema for prompt response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** | Prompt ID | [default to undefined]
**owner_id** | **string** | Owner user ID | [default to undefined]
**name** | **string** | Prompt name | [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**prompt_type** | [**PromptType**](PromptType.md) | Prompt type | [default to undefined]
**category** | [**PromptCategory**](PromptCategory.md) | Prompt category | [default to undefined]
**content** | **string** | Prompt content/template | [default to undefined]
**variables** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**template_format** | **string** | Template format | [default to undefined]
**input_schema** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**output_schema** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**max_length** | **number** |  | [optional] [default to undefined]
**min_length** | **number** |  | [optional] [default to undefined]
**required_variables** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**examples** | **Array&lt;{ [key: string]: any; }&gt;** |  | [optional] [default to undefined]
**test_cases** | **Array&lt;{ [key: string]: any; }&gt;** |  | [optional] [default to undefined]
**suggested_temperature** | **number** |  | [optional] [default to undefined]
**suggested_max_tokens** | **number** |  | [optional] [default to undefined]
**suggested_providers** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**is_chain** | **boolean** | Whether this is a chain prompt | [default to undefined]
**chain_steps** | **Array&lt;{ [key: string]: any; }&gt;** |  | [optional] [default to undefined]
**parent_prompt_id** | **string** |  | [optional] [default to undefined]
**version** | **number** | Prompt version | [default to undefined]
**is_latest** | **boolean** | Whether this is the latest version | [default to undefined]
**changelog** | **string** |  | [optional] [default to undefined]
**is_public** | **boolean** | Whether prompt is public | [default to undefined]
**rating** | **number** |  | [optional] [default to undefined]
**rating_count** | **number** | Number of ratings | [default to undefined]
**usage_count** | **number** | Usage count | [default to undefined]
**success_rate** | **number** |  | [optional] [default to undefined]
**avg_response_time_ms** | **number** |  | [optional] [default to undefined]
**last_used_at** | **string** |  | [optional] [default to undefined]
**total_tokens_used** | **number** | Total tokens used | [default to undefined]
**total_cost** | **number** | Total cost | [default to undefined]
**avg_tokens_per_use** | **number** |  | [optional] [default to undefined]
**tags** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**extra_metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**content_hash** | **string** | Content hash | [default to undefined]
**estimated_tokens** | **number** |  | [optional] [default to undefined]
**language** | **string** |  | [optional] [default to undefined]
**created_at** | **string** | Creation timestamp | [default to undefined]
**updated_at** | **string** | Last update timestamp | [default to undefined]

## Example

```typescript
import { PromptResponse } from 'chatter-sdk';

const instance: PromptResponse = {
    id,
    owner_id,
    name,
    description,
    prompt_type,
    category,
    content,
    variables,
    template_format,
    input_schema,
    output_schema,
    max_length,
    min_length,
    required_variables,
    examples,
    test_cases,
    suggested_temperature,
    suggested_max_tokens,
    suggested_providers,
    is_chain,
    chain_steps,
    parent_prompt_id,
    version,
    is_latest,
    changelog,
    is_public,
    rating,
    rating_count,
    usage_count,
    success_rate,
    avg_response_time_ms,
    last_used_at,
    total_tokens_used,
    total_cost,
    avg_tokens_per_use,
    tags,
    extra_metadata,
    content_hash,
    estimated_tokens,
    language,
    created_at,
    updated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
