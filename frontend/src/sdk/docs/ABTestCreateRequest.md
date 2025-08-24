# ABTestCreateRequest

Request schema for creating an A/B test.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | Test name | [default to undefined]
**description** | **string** | Test description | [default to undefined]
**test_type** | [**TestType**](TestType.md) | Type of test | [default to undefined]
**allocation_strategy** | [**VariantAllocation**](VariantAllocation.md) | Allocation strategy | [default to undefined]
**variants** | [**Array&lt;TestVariant&gt;**](TestVariant.md) | Test variants | [default to undefined]
**metrics** | [**Array&lt;MetricType&gt;**](MetricType.md) | Metrics to track | [default to undefined]
**duration_days** | **number** | Test duration in days | [optional] [default to 7]
**min_sample_size** | **number** | Minimum sample size | [optional] [default to 100]
**confidence_level** | **number** | Statistical confidence level | [optional] [default to 0.95]
**target_audience** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**traffic_percentage** | **number** | Percentage of traffic to include | [optional] [default to 100.0]
**tags** | **Array&lt;string&gt;** | Test tags | [optional] [default to undefined]
**metadata** | **{ [key: string]: any; }** | Additional metadata | [optional] [default to undefined]

## Example

```typescript
import { ABTestCreateRequest } from 'chatter-sdk';

const instance: ABTestCreateRequest = {
    name,
    description,
    test_type,
    allocation_strategy,
    variants,
    metrics,
    duration_days,
    min_sample_size,
    confidence_level,
    target_audience,
    traffic_percentage,
    tags,
    metadata,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
