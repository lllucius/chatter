# HealthCheckResponse

Schema for health check response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**HealthStatus**](HealthStatus.md) | Health status | [default to undefined]
**service** | **string** | Service name | [default to undefined]
**version** | **string** | Service version | [default to undefined]
**environment** | **string** | Environment | [default to undefined]

## Example

```typescript
import { HealthCheckResponse } from 'chatter-sdk';

const instance: HealthCheckResponse = {
    status,
    service,
    version,
    environment,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
