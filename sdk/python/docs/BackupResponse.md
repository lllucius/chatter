# BackupResponse

Response schema for backup data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Backup ID | 
**name** | **str** | Backup name | 
**description** | **str** |  | [optional] 
**backup_type** | [**BackupType**](BackupType.md) |  | 
**status** | **str** | Backup status | 
**file_size** | **int** |  | [optional] 
**compressed_size** | **int** |  | [optional] 
**record_count** | **int** |  | [optional] 
**created_at** | **datetime** | Backup creation timestamp | 
**completed_at** | **datetime** |  | [optional] 
**expires_at** | **datetime** |  | [optional] 
**encrypted** | **bool** | Whether backup is encrypted | 
**compressed** | **bool** | Whether backup is compressed | 
**metadata** | **Dict[str, object]** | Backup metadata | 

## Example

```python
from chatter_sdk.models.backup_response import BackupResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BackupResponse from a JSON string
backup_response_instance = BackupResponse.from_json(json)
# print the JSON string representation of the object
print(BackupResponse.to_json())

# convert the object into a dict
backup_response_dict = backup_response_instance.to_dict()
# create an instance of BackupResponse from a dict
backup_response_from_dict = BackupResponse.from_dict(backup_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


