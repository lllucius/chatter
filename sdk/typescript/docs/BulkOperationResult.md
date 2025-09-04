# BulkOperationResult

Schema for bulk operation results.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_requested** | **number** | Total servers requested | [default to undefined]
**successful** | **number** | Successfully processed | [default to undefined]
**failed** | **number** | Failed to process | [default to undefined]
**results** | **Array&lt;{ [key: string]: any; } | null&gt;** | Detailed results | [default to undefined]
**errors** | **Array&lt;string&gt;** | Error messages | [optional] [default to undefined]

## Example

```typescript
import { BulkOperationResult } from 'chatter-sdk';

const instance: BulkOperationResult = {
    total_requested,
    successful,
    failed,
    results,
    errors,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
