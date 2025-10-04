# WorkflowTemplateImportRequest

Schema for template import request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**template** | **Dict[str, object]** | Template data to import | 
**override_name** | **str** |  | [optional] 
**merge_with_existing** | **bool** | Whether to merge with existing template if found | [optional] [default to False]

## Example

```python
from chatter_sdk.models.workflow_template_import_request import WorkflowTemplateImportRequest

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowTemplateImportRequest from a JSON string
workflow_template_import_request_instance = WorkflowTemplateImportRequest.from_json(json)
# print the JSON string representation of the object
print(WorkflowTemplateImportRequest.to_json())

# convert the object into a dict
workflow_template_import_request_dict = workflow_template_import_request_instance.to_dict()
# create an instance of WorkflowTemplateImportRequest from a dict
workflow_template_import_request_from_dict = WorkflowTemplateImportRequest.from_dict(workflow_template_import_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


