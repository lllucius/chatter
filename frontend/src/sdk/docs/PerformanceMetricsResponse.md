# PerformanceMetricsResponse

Schema for performance metrics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**avg_response_time_ms** | **number** | Average response time | [default to undefined]
**median_response_time_ms** | **number** | Median response time | [default to undefined]
**p95_response_time_ms** | **number** | 95th percentile response time | [default to undefined]
**p99_response_time_ms** | **number** | 99th percentile response time | [default to undefined]
**requests_per_minute** | **number** | Average requests per minute | [default to undefined]
**tokens_per_minute** | **number** | Average tokens per minute | [default to undefined]
**total_errors** | **number** | Total number of errors | [default to undefined]
**error_rate** | **number** | Error rate percentage | [default to undefined]
**errors_by_type** | **{ [key: string]: number; }** | Errors grouped by type | [default to undefined]
**performance_by_model** | **{ [key: string]: { [key: string]: number; }; }** | Performance metrics by model | [default to undefined]
**performance_by_provider** | **{ [key: string]: { [key: string]: number; }; }** | Performance metrics by provider | [default to undefined]
**database_response_time_ms** | **number** | Average database response time | [default to undefined]
**vector_search_time_ms** | **number** | Average vector search time | [default to undefined]
**embedding_generation_time_ms** | **number** | Average embedding generation time | [default to undefined]

## Example

```typescript
import { PerformanceMetricsResponse } from 'chatter-sdk';

const instance: PerformanceMetricsResponse = {
    avg_response_time_ms,
    median_response_time_ms,
    p95_response_time_ms,
    p99_response_time_ms,
    requests_per_minute,
    tokens_per_minute,
    total_errors,
    error_rate,
    errors_by_type,
    performance_by_model,
    performance_by_provider,
    database_response_time_ms,
    vector_search_time_ms,
    embedding_generation_time_ms,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
