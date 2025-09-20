# WorkflowUpdateResponse

Schema for workflow update response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**workflow_id** | **str** | Workflow ID | 
**status** | **str** | Update status | 
**message** | **str** | Update message | 
**updated_fields** | **List[str]** | Fields that were updated | 

## Example

```python
from chatter_sdk.models.workflow_update_response import WorkflowUpdateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowUpdateResponse from a JSON string
workflow_update_response_instance = WorkflowUpdateResponse.from_json(json)
# print the JSON string representation of the object
print(WorkflowUpdateResponse.to_json())

# convert the object into a dict
workflow_update_response_dict = workflow_update_response_instance.to_dict()
# create an instance of WorkflowUpdateResponse from a dict
workflow_update_response_from_dict = WorkflowUpdateResponse.from_dict(workflow_update_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


