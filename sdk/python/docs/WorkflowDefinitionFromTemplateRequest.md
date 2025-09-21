# WorkflowDefinitionFromTemplateRequest

Schema for creating a workflow definition from a template.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**template_id** | **str** | Template ID to instantiate | 
**name_suffix** | **str** |  | [optional] 
**user_input** | **Dict[str, object]** |  | [optional] 
**is_temporary** | **bool** | Whether this is a temporary definition for execution | [optional] [default to True]

## Example

```python
from chatter_sdk.models.workflow_definition_from_template_request import WorkflowDefinitionFromTemplateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowDefinitionFromTemplateRequest from a JSON string
workflow_definition_from_template_request_instance = WorkflowDefinitionFromTemplateRequest.from_json(json)
# print the JSON string representation of the object
print(WorkflowDefinitionFromTemplateRequest.to_json())

# convert the object into a dict
workflow_definition_from_template_request_dict = workflow_definition_from_template_request_instance.to_dict()
# create an instance of WorkflowDefinitionFromTemplateRequest from a dict
workflow_definition_from_template_request_from_dict = WorkflowDefinitionFromTemplateRequest.from_dict(workflow_definition_from_template_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


