# RestoreRequest

Request schema for restoring from backup.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**backup_id** | **string** | Backup ID to restore from | [default to undefined]
**restore_options** | **{ [key: string]: any; }** | Restore options | [optional] [default to undefined]
**create_backup_before_restore** | **boolean** | Create backup before restore | [optional] [default to true]
**verify_integrity** | **boolean** | Verify backup integrity before restore | [optional] [default to true]

## Example

```typescript
import { RestoreRequest } from 'chatter-sdk';

const instance: RestoreRequest = {
    backup_id,
    restore_options,
    create_backup_before_restore,
    verify_integrity,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
