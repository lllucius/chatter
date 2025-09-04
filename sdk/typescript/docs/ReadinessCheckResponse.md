# ReadinessCheckResponse

Schema for readiness check response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ReadinessStatus**](ReadinessStatus.md) | Readiness status | [default to undefined]
**service** | **string** | Service name | [default to undefined]
**version** | **string** | Service version | [default to undefined]
**environment** | **string** | Environment | [default to undefined]
**checks** | **{ [key: string]: any; }** | Health check results | [default to undefined]

## Example

```typescript
import { ReadinessCheckResponse } from 'chatter-sdk';

const instance: ReadinessCheckResponse = {
    status,
    service,
    version,
    environment,
    checks,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
