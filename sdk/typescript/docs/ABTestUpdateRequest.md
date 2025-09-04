# ABTestUpdateRequest

Request schema for updating an A/B test.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**status** | [**TestStatus**](TestStatus.md) |  | [optional] [default to undefined]
**duration_days** | **number** |  | [optional] [default to undefined]
**min_sample_size** | **number** |  | [optional] [default to undefined]
**confidence_level** | **number** |  | [optional] [default to undefined]
**traffic_percentage** | **number** |  | [optional] [default to undefined]
**tags** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { ABTestUpdateRequest } from 'chatter-sdk';

const instance: ABTestUpdateRequest = {
    name,
    description,
    status,
    duration_days,
    min_sample_size,
    confidence_level,
    traffic_percentage,
    tags,
    metadata,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
