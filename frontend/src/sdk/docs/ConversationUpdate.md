# ConversationUpdate

Schema for updating a conversation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **string** |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**status** | [**ConversationStatus**](ConversationStatus.md) |  | [optional] [default to undefined]
**temperature** | **number** |  | [optional] [default to undefined]
**max_tokens** | **number** |  | [optional] [default to undefined]
**workflow_config** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**extra_metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { ConversationUpdate } from 'chatter-sdk';

const instance: ConversationUpdate = {
    title,
    description,
    status,
    temperature,
    max_tokens,
    workflow_config,
    extra_metadata,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
