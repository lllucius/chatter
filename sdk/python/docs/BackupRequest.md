# BackupRequest

Request schema for creating a backup via API.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**backup_type** | [**BackupType**](BackupType.md) |  | [optional] 
**name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**include_files** | **bool** | Include uploaded files | [optional] [default to True]
**include_logs** | **bool** | Include system logs | [optional] [default to False]
**compress** | **bool** | Compress backup | [optional] [default to True]
**encrypt** | **bool** | Encrypt backup | [optional] [default to True]
**retention_days** | **int** | Backup retention in days | [optional] [default to 30]

## Example

```python
from chatter_sdk.models.backup_request import BackupRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BackupRequest from a JSON string
backup_request_instance = BackupRequest.from_json(json)
# print the JSON string representation of the object
print(BackupRequest.to_json())

# convert the object into a dict
backup_request_dict = backup_request_instance.to_dict()
# create an instance of BackupRequest from a dict
backup_request_from_dict = BackupRequest.from_dict(backup_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


