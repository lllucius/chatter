# ABTestActionResponse

Response schema for test actions (start, pause, complete).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **boolean** | Whether action was successful | [default to undefined]
**message** | **string** | Action result message | [default to undefined]
**test_id** | **string** | Test ID | [default to undefined]
**new_status** | [**TestStatus**](TestStatus.md) | New test status | [default to undefined]

## Example

```typescript
import { ABTestActionResponse } from 'chatter-sdk';

const instance: ABTestActionResponse = {
    success,
    message,
    test_id,
    new_status,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
