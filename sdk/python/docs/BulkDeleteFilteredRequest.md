# BulkDeleteFilteredRequest

Request for server-side filtered bulk delete.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**filters** | [**BulkOperationFilters**](BulkOperationFilters.md) |  | 

## Example

```python
from chatter_sdk.models.bulk_delete_filtered_request import BulkDeleteFilteredRequest

# TODO update the JSON string below
json = "{}"
# create an instance of BulkDeleteFilteredRequest from a JSON string
bulk_delete_filtered_request_instance = BulkDeleteFilteredRequest.from_json(json)
# print the JSON string representation of the object
print(BulkDeleteFilteredRequest.to_json())

# convert the object into a dict
bulk_delete_filtered_request_dict = bulk_delete_filtered_request_instance.to_dict()
# create an instance of BulkDeleteFilteredRequest from a dict
bulk_delete_filtered_request_from_dict = BulkDeleteFilteredRequest.from_dict(bulk_delete_filtered_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


