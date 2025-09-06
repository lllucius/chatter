# BulkToolServerOperation

Schema for bulk operations on tool servers.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**server_ids** | **List[str]** | List of server IDs | 
**operation** | **str** | Operation to perform | 
**parameters** | **Dict[str, object]** |  | [optional] 

## Example

```python
from chatter_sdk.models.bulk_tool_server_operation import BulkToolServerOperation

# TODO update the JSON string below
json = "{}"
# create an instance of BulkToolServerOperation from a JSON string
bulk_tool_server_operation_instance = BulkToolServerOperation.from_json(json)
# print the JSON string representation of the object
print(BulkToolServerOperation.to_json())

# convert the object into a dict
bulk_tool_server_operation_dict = bulk_tool_server_operation_instance.to_dict()
# create an instance of BulkToolServerOperation from a dict
bulk_tool_server_operation_from_dict = BulkToolServerOperation.from_dict(bulk_tool_server_operation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


