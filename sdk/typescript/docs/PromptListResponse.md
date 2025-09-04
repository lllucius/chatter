# PromptListResponse

Schema for prompt list response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**prompts** | [**Array&lt;PromptResponse&gt;**](PromptResponse.md) | List of prompts | [default to undefined]
**total_count** | **number** | Total number of prompts | [default to undefined]
**limit** | **number** | Requested limit | [default to undefined]
**offset** | **number** | Requested offset | [default to undefined]

## Example

```typescript
import { PromptListResponse } from 'chatter-sdk';

const instance: PromptListResponse = {
    prompts,
    total_count,
    limit,
    offset,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
