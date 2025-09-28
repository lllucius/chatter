# WorkflowExecutionLogEntry

Schema for individual execution log entries.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**timestamp** | **datetime** | Log entry timestamp | 
**level** | **str** | Log level (DEBUG, INFO, WARN, ERROR) | 
**node_id** | **str** |  | [optional] 
**step_name** | **str** |  | [optional] 
**message** | **str** | Log message | 
**data** | **Dict[str, object]** |  | [optional] 
**execution_time_ms** | **int** |  | [optional] 

## Example

```python
from chatter_sdk.models.workflow_execution_log_entry import WorkflowExecutionLogEntry

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowExecutionLogEntry from a JSON string
workflow_execution_log_entry_instance = WorkflowExecutionLogEntry.from_json(json)
# print the JSON string representation of the object
print(WorkflowExecutionLogEntry.to_json())

# convert the object into a dict
workflow_execution_log_entry_dict = workflow_execution_log_entry_instance.to_dict()
# create an instance of WorkflowExecutionLogEntry from a dict
workflow_execution_log_entry_from_dict = WorkflowExecutionLogEntry.from_dict(workflow_execution_log_entry_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


