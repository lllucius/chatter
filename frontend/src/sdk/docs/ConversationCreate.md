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
**temperature** | **number** |  | [optional] [default to undefined]
**max_tokens** | **number** |  | [optional] [default to undefined]
**workflow_config** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**extra_metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { ConversationCreate } from 'chatter-sdk';

const instance: ConversationCreate = {
    title,
    description,
    profile_id,
    system_prompt,
    enable_retrieval,
    temperature,
    max_tokens,
    workflow_config,
    extra_metadata,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
