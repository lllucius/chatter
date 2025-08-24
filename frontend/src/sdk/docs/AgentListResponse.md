# AgentListResponse

Response schema for agent list.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**agents** | [**Array&lt;AgentResponse&gt;**](AgentResponse.md) | List of agents | [default to undefined]
**total** | **number** | Total number of agents | [default to undefined]

## Example

```typescript
import { AgentListResponse } from 'chatter-sdk';

const instance: AgentListResponse = {
    agents,
    total,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
