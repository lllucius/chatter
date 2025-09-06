# BackupListResponse

Response schema for backup list.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**backups** | [**List[BackupResponse]**](BackupResponse.md) | List of backups | 
**total** | **int** | Total number of backups | 

## Example

```python
from chatter_sdk.models.backup_list_response import BackupListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BackupListResponse from a JSON string
backup_list_response_instance = BackupListResponse.from_json(json)
# print the JSON string representation of the object
print(BackupListResponse.to_json())

# convert the object into a dict
backup_list_response_dict = backup_list_response_instance.to_dict()
# create an instance of BackupListResponse from a dict
backup_list_response_from_dict = BackupListResponse.from_dict(backup_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


