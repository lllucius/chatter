# SystemAnalyticsResponse

Schema for system analytics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_users** | **number** | Total number of users | [default to undefined]
**active_users_today** | **number** | Active users today | [default to undefined]
**active_users_week** | **number** | Active users this week | [default to undefined]
**active_users_month** | **number** | Active users this month | [default to undefined]
**system_uptime_seconds** | **number** | System uptime in seconds | [default to undefined]
**avg_cpu_usage** | **number** | Average CPU usage percentage | [default to undefined]
**avg_memory_usage** | **number** | Average memory usage percentage | [default to undefined]
**database_connections** | **number** | Current database connections | [default to undefined]
**total_api_requests** | **number** | Total API requests | [default to undefined]
**requests_per_endpoint** | **{ [key: string]: number; }** | Requests by endpoint | [default to undefined]
**avg_api_response_time** | **number** | Average API response time | [default to undefined]
**api_error_rate** | **number** | API error rate | [default to undefined]
**storage_usage_bytes** | **number** | Total storage usage | [default to undefined]
**vector_database_size_bytes** | **number** | Vector database size | [default to undefined]
**cache_hit_rate** | **number** | Cache hit rate | [default to undefined]

## Example

```typescript
import { SystemAnalyticsResponse } from 'chatter-sdk';

const instance: SystemAnalyticsResponse = {
    total_users,
    active_users_today,
    active_users_week,
    active_users_month,
    system_uptime_seconds,
    avg_cpu_usage,
    avg_memory_usage,
    database_connections,
    total_api_requests,
    requests_per_endpoint,
    avg_api_response_time,
    api_error_rate,
    storage_usage_bytes,
    vector_database_size_bytes,
    cache_hit_rate,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
