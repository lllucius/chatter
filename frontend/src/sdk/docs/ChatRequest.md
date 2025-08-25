# ChatRequest

Schema for chat request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **string** | User message | [default to undefined]
**conversation_id** | **string** |  | [optional] [default to undefined]
**profile_id** | **string** |  | [optional] [default to undefined]
**stream** | **boolean** | Enable streaming response | [optional] [default to false]
**temperature** | **number** |  | [optional] [default to undefined]
**max_tokens** | **number** |  | [optional] [default to undefined]
**enable_retrieval** | **boolean** |  | [optional] [default to undefined]
**document_ids** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**system_prompt_override** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { ChatRequest } from 'chatter-sdk';

const instance: ChatRequest = {
    message,
    conversation_id,
    profile_id,
    stream,
    temperature,
    max_tokens,
    enable_retrieval,
    document_ids,
    system_prompt_override,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
