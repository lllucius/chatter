# ConversationStatsResponse

Schema for conversation statistics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_conversations** | **number** | Total number of conversations | [default to undefined]
**conversations_by_status** | **{ [key: string]: number; }** | Conversations grouped by status | [default to undefined]
**total_messages** | **number** | Total number of messages | [default to undefined]
**messages_by_role** | **{ [key: string]: number; }** | Messages grouped by role | [default to undefined]
**avg_messages_per_conversation** | **number** | Average messages per conversation | [default to undefined]
**total_tokens_used** | **number** | Total tokens used | [default to undefined]
**total_cost** | **number** | Total cost incurred | [default to undefined]
**avg_response_time_ms** | **number** | Average response time in milliseconds | [default to undefined]
**conversations_by_date** | **{ [key: string]: number; }** | Conversations by date | [default to undefined]
**most_active_hours** | **{ [key: string]: number; }** | Most active hours | [default to undefined]
**popular_models** | **{ [key: string]: number; }** | Popular LLM models | [default to undefined]
**popular_providers** | **{ [key: string]: number; }** | Popular LLM providers | [default to undefined]

## Example

```typescript
import { ConversationStatsResponse } from 'chatter-sdk';

const instance: ConversationStatsResponse = {
    total_conversations,
    conversations_by_status,
    total_messages,
    messages_by_role,
    avg_messages_per_conversation,
    total_tokens_used,
    total_cost,
    avg_response_time_ms,
    conversations_by_date,
    most_active_hours,
    popular_models,
    popular_providers,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
