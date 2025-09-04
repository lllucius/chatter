# ConversationCreate

Schema for creating a conversation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **string** | Conversation title | [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**profile_id** | **string** |  | [optional] [default to undefined]
**system_prompt** | **string** |  | [optional] [default to undefined]
**enable_retrieval** | **boolean** | Enable document retrieval | [optional] [default to false]

## Example

```typescript
import { ConversationCreate } from 'chatter-sdk';

const instance: ConversationCreate = {
    title,
    description,
    profile_id,
    system_prompt,
    enable_retrieval,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
