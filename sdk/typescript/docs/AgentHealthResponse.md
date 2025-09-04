# AgentHealthResponse

Response schema for agent health check.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**agent_id** | **string** | Agent ID | [default to undefined]
**status** | [**AgentStatus**](AgentStatus.md) | Agent status | [default to undefined]
**health** | **string** | Health status (healthy/unhealthy/unknown) | [default to undefined]
**last_interaction** | **string** |  | [optional] [default to undefined]
**response_time_avg** | **number** |  | [optional] [default to undefined]
**error_rate** | **number** |  | [optional] [default to undefined]

## Example

```typescript
import { AgentHealthResponse } from 'chatter-sdk';

const instance: AgentHealthResponse = {
    agent_id,
    status,
    health,
    last_interaction,
    response_time_avg,
    error_rate,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
