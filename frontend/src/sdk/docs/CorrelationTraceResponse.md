# CorrelationTraceResponse

Schema for correlation trace response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**correlation_id** | **string** | Correlation ID | [default to undefined]
**trace_length** | **number** | Number of requests in trace | [default to undefined]
**requests** | **Array&lt;{ [key: string]: any; } | null&gt;** | List of requests in trace | [default to undefined]

## Example

```typescript
import { CorrelationTraceResponse } from 'chatter-sdk';

const instance: CorrelationTraceResponse = {
    correlation_id,
    trace_length,
    requests,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
