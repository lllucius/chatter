# RestoreResponse

Response schema for restore operation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**restore_id** | **string** | Restore operation ID | [default to undefined]
**backup_id** | **string** | Source backup ID | [default to undefined]
**status** | **string** | Restore status | [default to undefined]
**progress** | **number** | Restore progress percentage | [optional] [default to 0]
**records_restored** | **number** | Number of records restored | [optional] [default to 0]
**started_at** | **string** | Restore start timestamp | [default to undefined]
**completed_at** | **string** |  | [optional] [default to undefined]
**error_message** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { RestoreResponse } from 'chatter-sdk';

const instance: RestoreResponse = {
    restore_id,
    backup_id,
    status,
    progress,
    records_restored,
    started_at,
    completed_at,
    error_message,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
