# ABTestMetricsResponse

Response schema for A/B test metrics.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test_id** | **string** | Test ID | [default to undefined]
**metrics** | [**Array&lt;TestMetric&gt;**](TestMetric.md) | Current metrics | [default to undefined]
**participant_count** | **number** | Current participant count | [default to undefined]
**last_updated** | **string** | Last metrics update | [default to undefined]

## Example

```typescript
import { ABTestMetricsResponse } from 'chatter-sdk';

const instance: ABTestMetricsResponse = {
    test_id,
    metrics,
    participant_count,
    last_updated,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
