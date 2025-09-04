# DashboardResponse

Schema for analytics dashboard response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**conversation_stats** | [**ConversationStatsResponse**](ConversationStatsResponse.md) | Conversation statistics | [default to undefined]
**usage_metrics** | [**UsageMetricsResponse**](UsageMetricsResponse.md) | Usage metrics | [default to undefined]
**performance_metrics** | [**PerformanceMetricsResponse**](PerformanceMetricsResponse.md) | Performance metrics | [default to undefined]
**document_analytics** | [**DocumentAnalyticsResponse**](DocumentAnalyticsResponse.md) | Document analytics | [default to undefined]
**system_health** | [**SystemAnalyticsResponse**](SystemAnalyticsResponse.md) | System health metrics | [default to undefined]
**custom_metrics** | **Array&lt;{ [key: string]: any; } | null&gt;** | Custom metrics | [default to undefined]
**generated_at** | **string** | Dashboard generation time | [default to undefined]

## Example

```typescript
import { DashboardResponse } from 'chatter-sdk';

const instance: DashboardResponse = {
    conversation_stats,
    usage_metrics,
    performance_metrics,
    document_analytics,
    system_health,
    custom_metrics,
    generated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
