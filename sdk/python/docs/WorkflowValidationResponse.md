# WorkflowValidationResponse

Schema for workflow validation response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**is_valid** | **bool** | Whether workflow is valid | 
**errors** | [**List[ValidationError]**](ValidationError.md) | Validation errors | 
**warnings** | [**List[ValidationError]**](ValidationError.md) | Validation warnings | 
**suggestions** | **List[str]** | Validation suggestions | 

## Example

```python
from chatter_sdk.models.workflow_validation_response import WorkflowValidationResponse

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowValidationResponse from a JSON string
workflow_validation_response_instance = WorkflowValidationResponse.from_json(json)
# print the JSON string representation of the object
print(WorkflowValidationResponse.to_json())

# convert the object into a dict
workflow_validation_response_dict = workflow_validation_response_instance.to_dict()
# create an instance of WorkflowValidationResponse from a dict
workflow_validation_response_from_dict = WorkflowValidationResponse.from_dict(workflow_validation_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


