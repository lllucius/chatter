# AgentBulkCreateRequest

Request schema for bulk agent creation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**agents** | [**Array&lt;AgentCreateRequest&gt;**](AgentCreateRequest.md) | List of agents to create (max 10) | [default to undefined]

## Example

```typescript
import { AgentBulkCreateRequest } from 'chatter-sdk';

const instance: AgentBulkCreateRequest = {
    agents,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
