# BulkOperationResult

Schema for bulk operation results.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_requested** | **int** | Total servers requested | 
**successful** | **int** | Successfully processed | 
**failed** | **int** | Failed to process | 
**results** | **List[Dict[str, object]]** | Detailed results | 
**errors** | **List[str]** | Error messages | [optional] 

## Example

```python
from chatter_sdk.models.bulk_operation_result import BulkOperationResult

# TODO update the JSON string below
json = "{}"
# create an instance of BulkOperationResult from a JSON string
bulk_operation_result_instance = BulkOperationResult.from_json(json)
# print the JSON string representation of the object
print(BulkOperationResult.to_json())

# convert the object into a dict
bulk_operation_result_dict = bulk_operation_result_instance.to_dict()
# create an instance of BulkOperationResult from a dict
bulk_operation_result_from_dict = BulkOperationResult.from_dict(bulk_operation_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


