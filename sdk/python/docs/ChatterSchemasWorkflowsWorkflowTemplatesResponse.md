# ChatterSchemasWorkflowsWorkflowTemplatesResponse

Schema for workflow templates list response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**templates** | [**List[WorkflowTemplateResponse]**](WorkflowTemplateResponse.md) | Workflow templates | 
**total_count** | **int** | Total number of templates | 

## Example

```python
from chatter_sdk.models.chatter_schemas_workflows_workflow_templates_response import ChatterSchemasWorkflowsWorkflowTemplatesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ChatterSchemasWorkflowsWorkflowTemplatesResponse from a JSON string
chatter_schemas_workflows_workflow_templates_response_instance = ChatterSchemasWorkflowsWorkflowTemplatesResponse.from_json(json)
# print the JSON string representation of the object
print(ChatterSchemasWorkflowsWorkflowTemplatesResponse.to_json())

# convert the object into a dict
chatter_schemas_workflows_workflow_templates_response_dict = chatter_schemas_workflows_workflow_templates_response_instance.to_dict()
# create an instance of ChatterSchemasWorkflowsWorkflowTemplatesResponse from a dict
chatter_schemas_workflows_workflow_templates_response_from_dict = ChatterSchemasWorkflowsWorkflowTemplatesResponse.from_dict(chatter_schemas_workflows_workflow_templates_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


