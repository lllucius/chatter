# PromptStatsResponse

Schema for prompt statistics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_prompts** | **number** | Total number of prompts | [default to undefined]
**prompts_by_type** | **{ [key: string]: number; }** | Prompts by type | [default to undefined]
**prompts_by_category** | **{ [key: string]: number; }** | Prompts by category | [default to undefined]
**most_used_prompts** | [**Array&lt;PromptResponse&gt;**](PromptResponse.md) | Most used prompts | [default to undefined]
**recent_prompts** | [**Array&lt;PromptResponse&gt;**](PromptResponse.md) | Recently created prompts | [default to undefined]
**usage_stats** | **{ [key: string]: any; }** | Usage statistics | [default to undefined]

## Example

```typescript
import { PromptStatsResponse } from 'chatter-sdk';

const instance: PromptStatsResponse = {
    total_prompts,
    prompts_by_type,
    prompts_by_category,
    most_used_prompts,
    recent_prompts,
    usage_stats,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
