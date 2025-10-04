# WorkflowTemplateExecutionRequest

Schema for template execution request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**input_data** | **Dict[str, object]** |  | [optional] 
**debug_mode** | **bool** | Enable debug mode | [optional] [default to False]

## Example

```python
from chatter_sdk.models.workflow_template_execution_request import WorkflowTemplateExecutionRequest

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowTemplateExecutionRequest from a JSON string
workflow_template_execution_request_instance = WorkflowTemplateExecutionRequest.from_json(json)
# print the JSON string representation of the object
print(WorkflowTemplateExecutionRequest.to_json())

# convert the object into a dict
workflow_template_execution_request_dict = workflow_template_execution_request_instance.to_dict()
# create an instance of WorkflowTemplateExecutionRequest from a dict
workflow_template_execution_request_from_dict = WorkflowTemplateExecutionRequest.from_dict(workflow_template_execution_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


