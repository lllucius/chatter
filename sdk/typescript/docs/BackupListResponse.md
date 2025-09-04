# BackupListResponse

Response schema for backup list.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**backups** | [**Array&lt;BackupResponse&gt;**](BackupResponse.md) | List of backups | [default to undefined]
**total** | **number** | Total number of backups | [default to undefined]

## Example

```typescript
import { BackupListResponse } from 'chatter-sdk';

const instance: BackupListResponse = {
    backups,
    total,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
