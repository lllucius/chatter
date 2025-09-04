# SSEStatsResponse

Response schema for SSE service statistics.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_connections** | **number** | Total active connections | [default to undefined]
**your_connections** | **number** | Your active connections | [default to undefined]

## Example

```typescript
import { SSEStatsResponse } from 'chatter-sdk';

const instance: SSEStatsResponse = {
    total_connections,
    your_connections,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
