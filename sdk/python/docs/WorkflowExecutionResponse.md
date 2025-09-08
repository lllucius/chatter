# WorkflowExecutionResponse

Schema for workflow execution response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**input_data** | **Dict[str, object]** |  | [optional] 
**id** | **str** | Execution ID | 
**definition_id** | **str** | Workflow definition ID | 
**owner_id** | **str** | Owner user ID | 
**status** | **str** | Execution status | 
**started_at** | **datetime** |  | [optional] 
**completed_at** | **datetime** |  | [optional] 
**execution_time_ms** | **int** |  | [optional] 
**output_data** | **Dict[str, object]** |  | [optional] 
**error_message** | **str** |  | [optional] 
**tokens_used** | **int** | Total tokens used | [optional] [default to 0]
**cost** | **float** | Total cost | [optional] [default to 0.0]
**created_at** | **datetime** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 

## Example

```python
from chatter_sdk.models.workflow_execution_response import WorkflowExecutionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowExecutionResponse from a JSON string
workflow_execution_response_instance = WorkflowExecutionResponse.from_json(json)
# print the JSON string representation of the object
print(WorkflowExecutionResponse.to_json())

# convert the object into a dict
workflow_execution_response_dict = workflow_execution_response_instance.to_dict()
# create an instance of WorkflowExecutionResponse from a dict
workflow_execution_response_from_dict = WorkflowExecutionResponse.from_dict(workflow_execution_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


