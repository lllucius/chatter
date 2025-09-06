# RestoreResponse

Response schema for restore operation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**restore_id** | **str** | Restore operation ID | 
**backup_id** | **str** | Source backup ID | 
**status** | **str** | Restore status | 
**progress** | **int** | Restore progress percentage | [optional] [default to 0]
**records_restored** | **int** | Number of records restored | [optional] [default to 0]
**started_at** | **datetime** | Restore start timestamp | 
**completed_at** | **datetime** |  | [optional] 
**error_message** | **str** |  | [optional] 

## Example

```python
from chatter_sdk.models.restore_response import RestoreResponse

# TODO update the JSON string below
json = "{}"
# create an instance of RestoreResponse from a JSON string
restore_response_instance = RestoreResponse.from_json(json)
# print the JSON string representation of the object
print(RestoreResponse.to_json())

# convert the object into a dict
restore_response_dict = restore_response_instance.to_dict()
# create an instance of RestoreResponse from a dict
restore_response_from_dict = RestoreResponse.from_dict(restore_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


