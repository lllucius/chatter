# ConversationWithMessages

Schema for conversation with messages.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **string** | Conversation title | [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**id** | **string** | Conversation ID | [default to undefined]
**user_id** | **string** | User ID | [default to undefined]
**profile_id** | **string** |  | [optional] [default to undefined]
**status** | [**ConversationStatus**](ConversationStatus.md) | Conversation status | [default to undefined]
**llm_provider** | **string** |  | [optional] [default to undefined]
**llm_model** | **string** |  | [optional] [default to undefined]
**temperature** | **number** |  | [optional] [default to undefined]
**max_tokens** | **number** |  | [optional] [default to undefined]
**enable_retrieval** | **boolean** | Retrieval enabled | [default to undefined]
**message_count** | **number** | Number of messages | [default to undefined]
**total_tokens** | **number** | Total tokens used | [default to undefined]
**total_cost** | **number** | Total cost | [default to undefined]
**created_at** | **string** | Creation timestamp | [default to undefined]
**updated_at** | **string** | Last update timestamp | [default to undefined]
**last_message_at** | **string** |  | [optional] [default to undefined]
**messages** | [**Array&lt;MessageResponse&gt;**](MessageResponse.md) | Conversation messages | [optional] [default to undefined]

## Example

```typescript
import { ConversationWithMessages } from 'chatter-sdk';

const instance: ConversationWithMessages = {
    title,
    description,
    id,
    user_id,
    profile_id,
    status,
    llm_provider,
    llm_model,
    temperature,
    max_tokens,
    enable_retrieval,
    message_count,
    total_tokens,
    total_cost,
    created_at,
    updated_at,
    last_message_at,
    messages,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
