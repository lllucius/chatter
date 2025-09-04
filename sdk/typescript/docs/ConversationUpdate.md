# ConversationUpdate

Schema for updating a conversation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **string** |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**status** | [**ConversationStatus**](ConversationStatus.md) |  | [optional] [default to undefined]

## Example

```typescript
import { ConversationUpdate } from 'chatter-sdk';

const instance: ConversationUpdate = {
    title,
    description,
    status,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
