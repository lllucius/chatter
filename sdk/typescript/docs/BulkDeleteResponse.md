# BulkDeleteResponse

Response schema for bulk delete operations.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_requested** | **number** | Total number of items requested for deletion | [default to undefined]
**successful_deletions** | **number** | Number of successful deletions | [default to undefined]
**failed_deletions** | **number** | Number of failed deletions | [default to undefined]
**errors** | **Array&lt;string&gt;** | List of error messages for failed deletions | [default to undefined]

## Example

```typescript
import { BulkDeleteResponse } from 'chatter-sdk';

const instance: BulkDeleteResponse = {
    total_requested,
    successful_deletions,
    failed_deletions,
    errors,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
