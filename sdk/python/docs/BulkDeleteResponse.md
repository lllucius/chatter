# BulkDeleteResponse

Response schema for bulk delete operations.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_requested** | **int** | Total number of items requested for deletion | 
**successful_deletions** | **int** | Number of successful deletions | 
**failed_deletions** | **int** | Number of failed deletions | 
**errors** | **List[str]** | List of error messages for failed deletions | 

## Example

```python
from chatter_sdk.models.bulk_delete_response import BulkDeleteResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BulkDeleteResponse from a JSON string
bulk_delete_response_instance = BulkDeleteResponse.from_json(json)
# print the JSON string representation of the object
print(BulkDeleteResponse.to_json())

# convert the object into a dict
bulk_delete_response_dict = bulk_delete_response_instance.to_dict()
# create an instance of BulkDeleteResponse from a dict
bulk_delete_response_from_dict = BulkDeleteResponse.from_dict(bulk_delete_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


