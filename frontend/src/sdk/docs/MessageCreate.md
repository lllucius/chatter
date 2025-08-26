# MessageCreate

Schema for creating a message.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**role** | [**MessageRole**](MessageRole.md) | Message role | [default to undefined]
**content** | **string** | Message content | [default to undefined]

## Example

```typescript
import { MessageCreate } from 'chatter-sdk';

const instance: MessageCreate = {
    role,
    content,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
