# AgentBulkDeleteRequest

Request schema for bulk agent deletion.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**agent_ids** | **Array&lt;string&gt;** | List of agent IDs to delete (max 50) | [default to undefined]

## Example

```typescript
import { AgentBulkDeleteRequest } from 'chatter-sdk';

const instance: AgentBulkDeleteRequest = {
    agent_ids,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
