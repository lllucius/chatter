# StorageStatsResponse

Response schema for storage statistics.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_size** | **int** | Total storage used in bytes | 
**database_size** | **int** | Database size in bytes | 
**files_size** | **int** | Uploaded files size in bytes | 
**backups_size** | **int** | Backups size in bytes | 
**exports_size** | **int** | Exports size in bytes | 
**total_records** | **int** | Total number of records | 
**total_files** | **int** | Total number of files | 
**total_backups** | **int** | Total number of backups | 
**storage_by_type** | **Dict[str, int]** | Storage usage by data type | 
**storage_by_user** | **Dict[str, int]** | Storage usage by user | 
**growth_rate_mb_per_day** | **float** | Storage growth rate in MB per day | 
**projected_size_30_days** | **int** | Projected size in 30 days | 
**last_updated** | **datetime** | Statistics last updated timestamp | 

## Example

```python
from chatter_sdk.models.storage_stats_response import StorageStatsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of StorageStatsResponse from a JSON string
storage_stats_response_instance = StorageStatsResponse.from_json(json)
# print the JSON string representation of the object
print(StorageStatsResponse.to_json())

# convert the object into a dict
storage_stats_response_dict = storage_stats_response_instance.to_dict()
# create an instance of StorageStatsResponse from a dict
storage_stats_response_from_dict = StorageStatsResponse.from_dict(storage_stats_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


