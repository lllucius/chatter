# MetricsResponse

Schema for application metrics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**timestamp** | **string** | Metrics collection timestamp (ISO 8601) | [default to undefined]
**service** | **string** | Service name | [default to undefined]
**version** | **string** | Service version | [default to undefined]
**environment** | **string** | Environment | [default to undefined]
**health** | **{ [key: string]: any; }** | Health metrics | [default to undefined]
**performance** | **{ [key: string]: any; }** | Performance statistics | [default to undefined]
**endpoints** | **{ [key: string]: any; }** | Endpoint statistics | [default to undefined]

## Example

```typescript
import { MetricsResponse } from 'chatter-sdk';

const instance: MetricsResponse = {
    timestamp,
    service,
    version,
    environment,
    health,
    performance,
    endpoints,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
