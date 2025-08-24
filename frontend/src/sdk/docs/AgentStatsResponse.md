# AgentStatsResponse

Response schema for agent statistics.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_agents** | **number** | Total number of agents | [default to undefined]
**active_agents** | **number** | Number of active agents | [default to undefined]
**agent_types** | **{ [key: string]: number; }** | Agents by type | [default to undefined]
**total_interactions** | **number** | Total interactions across all agents | [default to undefined]

## Example

```typescript
import { AgentStatsResponse } from 'chatter-sdk';

const instance: AgentStatsResponse = {
    total_agents,
    active_agents,
    agent_types,
    total_interactions,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
