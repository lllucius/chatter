# MessageResponse

Schema for message response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**role** | [**MessageRole**](MessageRole.md) | Message role | [default to undefined]
**content** | **string** | Message content | [default to undefined]
**id** | **string** | Message ID | [default to undefined]
**conversation_id** | **string** | Conversation ID | [default to undefined]
**sequence_number** | **number** | Message sequence number | [default to undefined]
**prompt_tokens** | **number** |  | [optional] [default to undefined]
**completion_tokens** | **number** |  | [optional] [default to undefined]
**total_tokens** | **number** |  | [optional] [default to undefined]
**model_used** | **string** |  | [optional] [default to undefined]
**provider_used** | **string** |  | [optional] [default to undefined]
**response_time_ms** | **number** |  | [optional] [default to undefined]
**cost** | **number** |  | [optional] [default to undefined]
**finish_reason** | **string** |  | [optional] [default to undefined]
**created_at** | **string** | Creation timestamp | [default to undefined]

## Example

```typescript
import { MessageResponse } from 'chatter-sdk';

const instance: MessageResponse = {
    role,
    content,
    id,
    conversation_id,
    sequence_number,
    prompt_tokens,
    completion_tokens,
    total_tokens,
    model_used,
    provider_used,
    response_time_ms,
    cost,
    finish_reason,
    created_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
