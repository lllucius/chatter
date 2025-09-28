# DetailedWorkflowExecutionResponse

Schema for detailed workflow execution response with full debug info.

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
**execution_log** | **List[Dict[str, object]]** |  | [optional] 
**debug_info** | **Dict[str, object]** |  | [optional] 
**created_at** | **datetime** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 
**logs** | [**List[WorkflowExecutionLogEntry]**](WorkflowExecutionLogEntry.md) | Structured execution logs | [optional] 
**debug_details** | [**WorkflowDebugInfo**](WorkflowDebugInfo.md) |  | [optional] 

## Example

```python
from chatter_sdk.models.detailed_workflow_execution_response import DetailedWorkflowExecutionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DetailedWorkflowExecutionResponse from a JSON string
detailed_workflow_execution_response_instance = DetailedWorkflowExecutionResponse.from_json(json)
# print the JSON string representation of the object
print(DetailedWorkflowExecutionResponse.to_json())

# convert the object into a dict
detailed_workflow_execution_response_dict = detailed_workflow_execution_response_instance.to_dict()
# create an instance of DetailedWorkflowExecutionResponse from a dict
detailed_workflow_execution_response_from_dict = DetailedWorkflowExecutionResponse.from_dict(detailed_workflow_execution_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


