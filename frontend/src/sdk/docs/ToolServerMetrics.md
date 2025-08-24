# ToolServerMetrics

Schema for tool server metrics.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**server_id** | **string** | Server ID | [default to undefined]
**server_name** | **string** | Server name | [default to undefined]
**status** | [**ServerStatus**](ServerStatus.md) | Server status | [default to undefined]
**total_tools** | **number** | Total number of tools | [default to undefined]
**enabled_tools** | **number** | Number of enabled tools | [default to undefined]
**total_calls** | **number** | Total tool calls | [default to undefined]
**total_errors** | **number** | Total errors | [default to undefined]
**success_rate** | **number** | Success rate | [default to undefined]
**avg_response_time_ms** | **number** |  | [optional] [default to undefined]
**last_activity** | **string** |  | [optional] [default to undefined]
**uptime_percentage** | **number** |  | [optional] [default to undefined]

## Example

```typescript
import { ToolServerMetrics } from 'chatter-sdk';

const instance: ToolServerMetrics = {
    server_id,
    server_name,
    status,
    total_tools,
    enabled_tools,
    total_calls,
    total_errors,
    success_rate,
    avg_response_time_ms,
    last_activity,
    uptime_percentage,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
