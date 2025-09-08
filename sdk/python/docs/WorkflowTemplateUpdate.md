# WorkflowTemplateUpdate

Schema for updating a workflow template.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**category** | **str** |  | [optional] 
**default_params** | **Dict[str, object]** |  | [optional] 
**required_tools** | **List[str]** |  | [optional] 
**required_retrievers** | **List[str]** |  | [optional] 
**tags** | **List[str]** |  | [optional] 
**is_public** | **bool** |  | [optional] 

## Example

```python
from chatter_sdk.models.workflow_template_update import WorkflowTemplateUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowTemplateUpdate from a JSON string
workflow_template_update_instance = WorkflowTemplateUpdate.from_json(json)
# print the JSON string representation of the object
print(WorkflowTemplateUpdate.to_json())

# convert the object into a dict
workflow_template_update_dict = workflow_template_update_instance.to_dict()
# create an instance of WorkflowTemplateUpdate from a dict
workflow_template_update_from_dict = WorkflowTemplateUpdate.from_dict(workflow_template_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


