# TestMetric

Test metric data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**metric_type** | [**MetricType**](MetricType.md) | Type of metric | [default to undefined]
**variant_name** | **string** | Variant name | [default to undefined]
**value** | **number** | Metric value | [default to undefined]
**sample_size** | **number** | Sample size | [default to undefined]
**confidence_interval** | **Array&lt;number&gt;** |  | [optional] [default to undefined]

## Example

```typescript
import { TestMetric } from 'chatter-sdk';

const instance: TestMetric = {
    metric_type,
    variant_name,
    value,
    sample_size,
    confidence_interval,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
