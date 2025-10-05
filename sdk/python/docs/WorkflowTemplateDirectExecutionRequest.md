# WorkflowTemplateDirectExecutionRequest

Schema for executing a temporary template directly.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**template** | **Dict[str, object]** | Template data to execute | 
**input_data** | **Dict[str, object]** |  | [optional] 
**debug_mode** | **bool** | Enable debug mode | [optional] [default to False]

## Example

```python
from chatter_sdk.models.workflow_template_direct_execution_request import WorkflowTemplateDirectExecutionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowTemplateDirectExecutionRequest from a JSON string
workflow_template_direct_execution_request_instance = WorkflowTemplateDirectExecutionRequest.from_json(json)
# print the JSON string representation of the object
print(WorkflowTemplateDirectExecutionRequest.to_json())

# convert the object into a dict
workflow_template_direct_execution_request_dict = workflow_template_direct_execution_request_instance.to_dict()
# create an instance of WorkflowTemplateDirectExecutionRequest from a dict
workflow_template_direct_execution_request_from_dict = WorkflowTemplateDirectExecutionRequest.from_dict(workflow_template_direct_execution_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


