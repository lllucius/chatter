# BulkDeletePreviewResponse

Response for bulk delete preview (dry run).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**entity_type** | [**EntityType**](EntityType.md) |  | 
**total_matching** | **int** | Total items matching filters | 
**sample_items** | **List[Dict[str, object]]** | Sample of items that would be deleted (first 10) | 
**filters_applied** | [**BulkOperationFilters**](BulkOperationFilters.md) |  | 

## Example

```python
from chatter_sdk.models.bulk_delete_preview_response import BulkDeletePreviewResponse

# TODO update the JSON string below
json = "{}"
# create an instance of BulkDeletePreviewResponse from a JSON string
bulk_delete_preview_response_instance = BulkDeletePreviewResponse.from_json(json)
# print the JSON string representation of the object
print(BulkDeletePreviewResponse.to_json())

# convert the object into a dict
bulk_delete_preview_response_dict = bulk_delete_preview_response_instance.to_dict()
# create an instance of BulkDeletePreviewResponse from a dict
bulk_delete_preview_response_from_dict = BulkDeletePreviewResponse.from_dict(bulk_delete_preview_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


