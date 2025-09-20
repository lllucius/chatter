# WorkflowDeleteResponse

Response schema for workflow deletion.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Deletion confirmation message | 
**workflow_id** | **str** | ID of the deleted workflow | 

## Example

```python
from chatter_sdk.models.workflow_delete_response import WorkflowDeleteResponse

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowDeleteResponse from a JSON string
workflow_delete_response_instance = WorkflowDeleteResponse.from_json(json)
# print the JSON string representation of the object
print(WorkflowDeleteResponse.to_json())

# convert the object into a dict
workflow_delete_response_dict = workflow_delete_response_instance.to_dict()
# create an instance of WorkflowDeleteResponse from a dict
workflow_delete_response_from_dict = WorkflowDeleteResponse.from_dict(workflow_delete_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


