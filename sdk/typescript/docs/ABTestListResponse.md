# ABTestListResponse

Response schema for A/B test list.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tests** | [**Array&lt;ABTestResponse&gt;**](ABTestResponse.md) | List of tests | [default to undefined]
**total** | **number** | Total number of tests | [default to undefined]

## Example

```typescript
import { ABTestListResponse } from 'chatter-sdk';

const instance: ABTestListResponse = {
    tests,
    total,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
