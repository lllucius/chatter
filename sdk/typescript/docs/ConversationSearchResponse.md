# ConversationSearchResponse

Schema for conversation search response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**conversations** | [**Array&lt;ConversationResponse&gt;**](ConversationResponse.md) | Conversations | [default to undefined]
**total** | **number** | Total number of conversations | [default to undefined]
**limit** | **number** | Request limit | [default to undefined]
**offset** | **number** | Request offset | [default to undefined]

## Example

```typescript
import { ConversationSearchResponse } from 'chatter-sdk';

const instance: ConversationSearchResponse = {
    conversations,
    total,
    limit,
    offset,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
