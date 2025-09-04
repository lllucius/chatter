# AgentInteractResponse

Response schema for agent interaction.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**agent_id** | **string** | Agent ID | [default to undefined]
**response** | **string** | Agent response | [default to undefined]
**conversation_id** | **string** | Conversation ID | [default to undefined]
**tools_used** | **Array&lt;string&gt;** | Tools used in response | [default to undefined]
**confidence_score** | **number** | Confidence score | [default to undefined]
**response_time** | **number** | Response time in seconds | [default to undefined]
**timestamp** | **string** | Response timestamp | [default to undefined]

## Example

```typescript
import { AgentInteractResponse } from 'chatter-sdk';

const instance: AgentInteractResponse = {
    agent_id,
    response,
    conversation_id,
    tools_used,
    confidence_score,
    response_time,
    timestamp,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
