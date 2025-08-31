# PerformanceStatsResponse

Schema for performance statistics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_executions** | **number** | Total number of executions | [default to undefined]
**avg_execution_time_ms** | **number** | Average execution time in milliseconds | [default to undefined]
**min_execution_time_ms** | **number** | Minimum execution time in milliseconds | [default to undefined]
**max_execution_time_ms** | **number** | Maximum execution time in milliseconds | [default to undefined]
**workflow_types** | **{ [key: string]: number; }** | Execution count by workflow type | [default to undefined]
**error_counts** | **{ [key: string]: number; }** | Error count by type | [default to undefined]
**cache_stats** | **{ [key: string]: any; }** | Cache statistics | [default to undefined]
**tool_stats** | **{ [key: string]: any; }** | Tool usage statistics | [default to undefined]
**timestamp** | **number** | Statistics timestamp | [default to undefined]

## Example

```typescript
import { PerformanceStatsResponse } from 'chatter-sdk';

const instance: PerformanceStatsResponse = {
    total_executions,
    avg_execution_time_ms,
    min_execution_time_ms,
    max_execution_time_ms,
    workflow_types,
    error_counts,
    cache_stats,
    tool_stats,
    timestamp,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
