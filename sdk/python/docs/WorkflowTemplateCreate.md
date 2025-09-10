# WorkflowTemplateCreate

Schema for creating a workflow template.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Template name | 
**description** | **str** | Template description | 
**workflow_type** | **str** | Workflow type | 
**category** | **str** | Template category | [optional] [default to 'custom']
**default_params** | **Dict[str, object]** | Default parameters | [optional] 
**required_tools** | **List[str]** |  | [optional] 
**required_retrievers** | **List[str]** |  | [optional] 
**tags** | **List[str]** |  | [optional] 
**is_public** | **bool** | Whether template is public | [optional] [default to False]
**workflow_definition_id** | **str** |  | [optional] 
**base_template_id** | **str** |  | [optional] 

## Example

```python
from chatter_sdk.models.workflow_template_create import WorkflowTemplateCreate

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowTemplateCreate from a JSON string
workflow_template_create_instance = WorkflowTemplateCreate.from_json(json)
# print the JSON string representation of the object
print(WorkflowTemplateCreate.to_json())

# convert the object into a dict
workflow_template_create_dict = workflow_template_create_instance.to_dict()
# create an instance of WorkflowTemplateCreate from a dict
workflow_template_create_from_dict = WorkflowTemplateCreate.from_dict(workflow_template_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


