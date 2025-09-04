# UsageMetricsResponse

Schema for usage metrics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_prompt_tokens** | **number** | Total prompt tokens | [default to undefined]
**total_completion_tokens** | **number** | Total completion tokens | [default to undefined]
**total_tokens** | **number** | Total tokens used | [default to undefined]
**tokens_by_model** | **{ [key: string]: number; }** | Token usage by model | [default to undefined]
**tokens_by_provider** | **{ [key: string]: number; }** | Token usage by provider | [default to undefined]
**total_cost** | **number** | Total cost | [default to undefined]
**cost_by_model** | **{ [key: string]: number; }** | Cost by model | [default to undefined]
**cost_by_provider** | **{ [key: string]: number; }** | Cost by provider | [default to undefined]
**daily_usage** | **{ [key: string]: number; }** | Daily token usage | [default to undefined]
**daily_cost** | **{ [key: string]: number; }** | Daily cost | [default to undefined]
**avg_response_time** | **number** | Average response time | [default to undefined]
**response_times_by_model** | **{ [key: string]: number; }** | Response times by model | [default to undefined]
**active_days** | **number** | Number of active days | [default to undefined]
**peak_usage_hour** | **number** | Peak usage hour | [default to undefined]
**conversations_per_day** | **number** | Average conversations per day | [default to undefined]

## Example

```typescript
import { UsageMetricsResponse } from 'chatter-sdk';

const instance: UsageMetricsResponse = {
    total_prompt_tokens,
    total_completion_tokens,
    total_tokens,
    tokens_by_model,
    tokens_by_provider,
    total_cost,
    cost_by_model,
    cost_by_provider,
    daily_usage,
    daily_cost,
    avg_response_time,
    response_times_by_model,
    active_days,
    peak_usage_hour,
    conversations_per_day,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
