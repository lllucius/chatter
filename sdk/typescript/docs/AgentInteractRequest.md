# AgentInteractRequest

Request schema for interacting with an agent.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **string** | Message to send to the agent | [default to undefined]
**conversation_id** | **string** | Conversation ID | [default to undefined]
**context** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { AgentInteractRequest } from 'chatter-sdk';

const instance: AgentInteractRequest = {
    message,
    conversation_id,
    context,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
