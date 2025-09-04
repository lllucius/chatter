# BackupResponse

Response schema for backup data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** | Backup ID | [default to undefined]
**name** | **string** | Backup name | [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**backup_type** | [**BackupType**](BackupType.md) | Backup type | [default to undefined]
**status** | **string** | Backup status | [default to undefined]
**file_size** | **number** |  | [optional] [default to undefined]
**compressed_size** | **number** |  | [optional] [default to undefined]
**record_count** | **number** |  | [optional] [default to undefined]
**created_at** | **string** | Backup creation timestamp | [default to undefined]
**completed_at** | **string** |  | [optional] [default to undefined]
**expires_at** | **string** |  | [optional] [default to undefined]
**encrypted** | **boolean** | Whether backup is encrypted | [default to undefined]
**compressed** | **boolean** | Whether backup is compressed | [default to undefined]
**metadata** | **{ [key: string]: any; }** | Backup metadata | [default to undefined]

## Example

```typescript
import { BackupResponse } from 'chatter-sdk';

const instance: BackupResponse = {
    id,
    name,
    description,
    backup_type,
    status,
    file_size,
    compressed_size,
    record_count,
    created_at,
    completed_at,
    expires_at,
    encrypted,
    compressed,
    metadata,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
