# WorkflowTemplateInfo

Schema for workflow template information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Template name | 
**workflow_type** | **str** | Workflow type | 
**description** | **str** | Template description | 
**required_tools** | **List[str]** | Required tools | 
**required_retrievers** | **List[str]** | Required retrievers | 
**default_params** | **Dict[str, object]** | Default parameters | 

## Example

```python
from chatter_sdk.models.workflow_template_info import WorkflowTemplateInfo

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowTemplateInfo from a JSON string
workflow_template_info_instance = WorkflowTemplateInfo.from_json(json)
# print the JSON string representation of the object
print(WorkflowTemplateInfo.to_json())

# convert the object into a dict
workflow_template_info_dict = workflow_template_info_instance.to_dict()
# create an instance of WorkflowTemplateInfo from a dict
workflow_template_info_from_dict = WorkflowTemplateInfo.from_dict(workflow_template_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


