# WorkflowTemplateValidationRequest

Schema for template validation request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**template** | **Dict[str, object]** | Template data to validate | 

## Example

```python
from chatter_sdk.models.workflow_template_validation_request import WorkflowTemplateValidationRequest

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowTemplateValidationRequest from a JSON string
workflow_template_validation_request_instance = WorkflowTemplateValidationRequest.from_json(json)
# print the JSON string representation of the object
print(WorkflowTemplateValidationRequest.to_json())

# convert the object into a dict
workflow_template_validation_request_dict = workflow_template_validation_request_instance.to_dict()
# create an instance of WorkflowTemplateValidationRequest from a dict
workflow_template_validation_request_from_dict = WorkflowTemplateValidationRequest.from_dict(workflow_template_validation_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


