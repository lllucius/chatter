# ABTestResponse

Response schema for A/B test data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** | Test ID | [default to undefined]
**name** | **string** | Test name | [default to undefined]
**description** | **string** | Test description | [default to undefined]
**test_type** | [**TestType**](TestType.md) | Type of test | [default to undefined]
**status** | [**TestStatus**](TestStatus.md) | Test status | [default to undefined]
**allocation_strategy** | [**VariantAllocation**](VariantAllocation.md) | Allocation strategy | [default to undefined]
**variants** | [**Array&lt;TestVariant&gt;**](TestVariant.md) | Test variants | [default to undefined]
**metrics** | [**Array&lt;MetricType&gt;**](MetricType.md) | Metrics being tracked | [default to undefined]
**duration_days** | **number** | Test duration in days | [default to undefined]
**min_sample_size** | **number** | Minimum sample size | [default to undefined]
**confidence_level** | **number** | Statistical confidence level | [default to undefined]
**target_audience** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**traffic_percentage** | **number** | Percentage of traffic included | [default to undefined]
**start_date** | **string** |  | [optional] [default to undefined]
**end_date** | **string** |  | [optional] [default to undefined]
**participant_count** | **number** | Number of participants | [optional] [default to 0]
**created_at** | **string** | Creation timestamp | [default to undefined]
**updated_at** | **string** | Last update timestamp | [default to undefined]
**created_by** | **string** | Creator | [default to undefined]
**tags** | **Array&lt;string&gt;** | Test tags | [default to undefined]
**metadata** | **{ [key: string]: any; }** | Additional metadata | [default to undefined]

## Example

```typescript
import { ABTestResponse } from 'chatter-sdk';

const instance: ABTestResponse = {
    id,
    name,
    description,
    test_type,
    status,
    allocation_strategy,
    variants,
    metrics,
    duration_days,
    min_sample_size,
    confidence_level,
    target_audience,
    traffic_percentage,
    start_date,
    end_date,
    participant_count,
    created_at,
    updated_at,
    created_by,
    tags,
    metadata,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
