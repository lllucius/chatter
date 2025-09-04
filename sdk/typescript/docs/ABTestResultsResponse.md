# ABTestResultsResponse

Response schema for A/B test results.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test_id** | **string** | Test ID | [default to undefined]
**test_name** | **string** | Test name | [default to undefined]
**status** | [**TestStatus**](TestStatus.md) | Test status | [default to undefined]
**metrics** | [**Array&lt;TestMetric&gt;**](TestMetric.md) | Metric results by variant | [default to undefined]
**statistical_significance** | **{ [key: string]: boolean; }** | Statistical significance by metric | [default to undefined]
**confidence_intervals** | **{ [key: string]: { [key: string]: Array&lt;number&gt;; }; }** | Confidence intervals | [default to undefined]
**winning_variant** | **string** |  | [optional] [default to undefined]
**recommendation** | **string** | Action recommendation | [default to undefined]
**generated_at** | **string** | Results generation timestamp | [default to undefined]
**sample_size** | **number** | Total sample size | [default to undefined]
**duration_days** | **number** | Test duration so far | [default to undefined]

## Example

```typescript
import { ABTestResultsResponse } from 'chatter-sdk';

const instance: ABTestResultsResponse = {
    test_id,
    test_name,
    status,
    metrics,
    statistical_significance,
    confidence_intervals,
    winning_variant,
    recommendation,
    generated_at,
    sample_size,
    duration_days,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
