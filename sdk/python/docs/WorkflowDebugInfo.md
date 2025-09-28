# WorkflowDebugInfo

Schema for workflow debug information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**workflow_structure** | **Dict[str, object]** | Workflow nodes and edges structure | 
**execution_path** | **List[str]** | Actual path taken through the workflow | 
**node_executions** | **List[Dict[str, object]]** | Details of each node execution | 
**variable_states** | **Dict[str, object]** | Variable states throughout execution | 
**performance_metrics** | **Dict[str, object]** | Performance metrics for each step | 
**llm_interactions** | **List[Dict[str, object]]** | LLM API interactions | [optional] 
**tool_calls** | **List[Dict[str, object]]** | Tool execution details | [optional] 

## Example

```python
from chatter_sdk.models.workflow_debug_info import WorkflowDebugInfo

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowDebugInfo from a JSON string
workflow_debug_info_instance = WorkflowDebugInfo.from_json(json)
# print the JSON string representation of the object
print(WorkflowDebugInfo.to_json())

# convert the object into a dict
workflow_debug_info_dict = workflow_debug_info_instance.to_dict()
# create an instance of WorkflowDebugInfo from a dict
workflow_debug_info_from_dict = WorkflowDebugInfo.from_dict(workflow_debug_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


