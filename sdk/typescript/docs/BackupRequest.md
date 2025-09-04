# BackupRequest

Request schema for creating a backup via API.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**backup_type** | [**BackupType**](BackupType.md) | Backup type | [optional] [default to undefined]
**name** | **string** |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**include_files** | **boolean** | Include uploaded files | [optional] [default to true]
**include_logs** | **boolean** | Include system logs | [optional] [default to false]
**compress** | **boolean** | Compress backup | [optional] [default to true]
**encrypt** | **boolean** | Encrypt backup | [optional] [default to true]
**retention_days** | **number** | Backup retention in days | [optional] [default to 30]

## Example

```typescript
import { BackupRequest } from 'chatter-sdk';

const instance: BackupRequest = {
    backup_type,
    name,
    description,
    include_files,
    include_logs,
    compress,
    encrypt,
    retention_days,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
