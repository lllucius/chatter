# ChatRequest

Schema for chat request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **string** | User message | [default to undefined]
**conversation_id** | **string** |  | [optional] [default to undefined]
**profile_id** | **string** |  | [optional] [default to undefined]
**stream** | **boolean** | Enable streaming response | [optional] [default to false]
**workflow** | **string** | Workflow type: plain, rag, tools, or full (rag + tools) | [optional] [default to Workflow_plain]
**provider** | **string** |  | [optional] [default to undefined]
**temperature** | **number** |  | [optional] [default to undefined]
**max_tokens** | **number** |  | [optional] [default to undefined]
**context_limit** | **number** |  | [optional] [default to undefined]
**enable_retrieval** | **boolean** |  | [optional] [default to undefined]
**document_ids** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**system_prompt_override** | **string** |  | [optional] [default to undefined]
**workflow_config** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**workflow_type** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { ChatRequest } from 'chatter-sdk';

const instance: ChatRequest = {
    message,
    conversation_id,
    profile_id,
    stream,
    workflow,
    provider,
    temperature,
    max_tokens,
    context_limit,
    enable_retrieval,
    document_ids,
    system_prompt_override,
    workflow_config,
    workflow_type,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
