# WorkflowTemplatesResponse

Schema for workflow templates list response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**templates** | [**List[WorkflowTemplateResponse]**](WorkflowTemplateResponse.md) | Workflow templates | 
**total_count** | **int** | Total number of templates | 

## Example

```python
from chatter_sdk.models.workflow_templates_response import WorkflowTemplatesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowTemplatesResponse from a JSON string
workflow_templates_response_instance = WorkflowTemplatesResponse.from_json(json)
# print the JSON string representation of the object
print(WorkflowTemplatesResponse.to_json())

# convert the object into a dict
workflow_templates_response_dict = workflow_templates_response_instance.to_dict()
# create an instance of WorkflowTemplatesResponse from a dict
workflow_templates_response_from_dict = WorkflowTemplatesResponse.from_dict(workflow_templates_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


