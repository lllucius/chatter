# WorkflowTemplateValidationResponse

Schema for template validation response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**is_valid** | **bool** | Whether template is valid | 
**errors** | **List[str]** | Validation errors | [optional] 
**warnings** | **List[str]** | Validation warnings | [optional] 
**template_info** | **Dict[str, object]** |  | [optional] 

## Example

```python
from chatter_sdk.models.workflow_template_validation_response import WorkflowTemplateValidationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowTemplateValidationResponse from a JSON string
workflow_template_validation_response_instance = WorkflowTemplateValidationResponse.from_json(json)
# print the JSON string representation of the object
print(WorkflowTemplateValidationResponse.to_json())

# convert the object into a dict
workflow_template_validation_response_dict = workflow_template_validation_response_instance.to_dict()
# create an instance of WorkflowTemplateValidationResponse from a dict
workflow_template_validation_response_from_dict = WorkflowTemplateValidationResponse.from_dict(workflow_template_validation_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


