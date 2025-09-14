# BulkOperationFilters

Server-side filters for bulk operations.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**entity_type** | [**EntityType**](EntityType.md) |  | 
**created_before** | **datetime** |  | [optional] 
**created_after** | **datetime** |  | [optional] 
**user_id** | **str** |  | [optional] 
**status** | **str** |  | [optional] 
**limit** | **int** | Maximum number of items to process | [optional] [default to 1000]
**dry_run** | **bool** | If true, only return count without deleting | [optional] [default to False]

## Example

```python
from chatter_sdk.models.bulk_operation_filters import BulkOperationFilters

# TODO update the JSON string below
json = "{}"
# create an instance of BulkOperationFilters from a JSON string
bulk_operation_filters_instance = BulkOperationFilters.from_json(json)
# print the JSON string representation of the object
print(BulkOperationFilters.to_json())

# convert the object into a dict
bulk_operation_filters_dict = bulk_operation_filters_instance.to_dict()
# create an instance of BulkOperationFilters from a dict
bulk_operation_filters_from_dict = BulkOperationFilters.from_dict(bulk_operation_filters_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


