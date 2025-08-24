# StorageStatsResponse

Response schema for storage statistics.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_size** | **number** | Total storage used in bytes | [default to undefined]
**database_size** | **number** | Database size in bytes | [default to undefined]
**files_size** | **number** | Uploaded files size in bytes | [default to undefined]
**backups_size** | **number** | Backups size in bytes | [default to undefined]
**exports_size** | **number** | Exports size in bytes | [default to undefined]
**total_records** | **number** | Total number of records | [default to undefined]
**total_files** | **number** | Total number of files | [default to undefined]
**total_backups** | **number** | Total number of backups | [default to undefined]
**storage_by_type** | **{ [key: string]: number; }** | Storage usage by data type | [default to undefined]
**storage_by_user** | **{ [key: string]: number; }** | Storage usage by user | [default to undefined]
**growth_rate_mb_per_day** | **number** | Storage growth rate in MB per day | [default to undefined]
**projected_size_30_days** | **number** | Projected size in 30 days | [default to undefined]
**last_updated** | **string** | Statistics last updated timestamp | [default to undefined]

## Example

```typescript
import { StorageStatsResponse } from 'chatter-sdk';

const instance: StorageStatsResponse = {
    total_size,
    database_size,
    files_size,
    backups_size,
    exports_size,
    total_records,
    total_files,
    total_backups,
    storage_by_type,
    storage_by_user,
    growth_rate_mb_per_day,
    projected_size_30_days,
    last_updated,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
