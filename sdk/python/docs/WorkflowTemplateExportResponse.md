# WorkflowTemplateExportResponse

Schema for template export response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**template** | **Dict[str, object]** | Complete template data including metadata | 
**export_format** | **str** | Export format version | [optional] [default to 'json']
**exported_at** | **datetime** | Export timestamp | 

## Example

```python
from chatter_sdk.models.workflow_template_export_response import WorkflowTemplateExportResponse

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowTemplateExportResponse from a JSON string
workflow_template_export_response_instance = WorkflowTemplateExportResponse.from_json(json)
# print the JSON string representation of the object
print(WorkflowTemplateExportResponse.to_json())

# convert the object into a dict
workflow_template_export_response_dict = workflow_template_export_response_instance.to_dict()
# create an instance of WorkflowTemplateExportResponse from a dict
workflow_template_export_response_from_dict = WorkflowTemplateExportResponse.from_dict(workflow_template_export_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


