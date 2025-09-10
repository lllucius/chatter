# WorkflowExecutionRequest

Schema for starting a workflow execution.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**input_data** | **Dict[str, object]** |  | [optional] 
**definition_id** | **str** | Workflow definition ID | 

## Example

```python
from chatter_sdk.models.workflow_execution_request import WorkflowExecutionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowExecutionRequest from a JSON string
workflow_execution_request_instance = WorkflowExecutionRequest.from_json(json)
# print the JSON string representation of the object
print(WorkflowExecutionRequest.to_json())

# convert the object into a dict
workflow_execution_request_dict = workflow_execution_request_instance.to_dict()
# create an instance of WorkflowExecutionRequest from a dict
workflow_execution_request_from_dict = WorkflowExecutionRequest.from_dict(workflow_execution_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


