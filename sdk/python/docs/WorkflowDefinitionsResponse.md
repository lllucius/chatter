# WorkflowDefinitionsResponse

Schema for workflow definitions list response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**definitions** | [**List[WorkflowDefinitionResponse]**](WorkflowDefinitionResponse.md) | Workflow definitions | 
**total_count** | **int** | Total number of definitions | 

## Example

```python
from chatter_sdk.models.workflow_definitions_response import WorkflowDefinitionsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowDefinitionsResponse from a JSON string
workflow_definitions_response_instance = WorkflowDefinitionsResponse.from_json(json)
# print the JSON string representation of the object
print(WorkflowDefinitionsResponse.to_json())

# convert the object into a dict
workflow_definitions_response_dict = workflow_definitions_response_instance.to_dict()
# create an instance of WorkflowDefinitionsResponse from a dict
workflow_definitions_response_from_dict = WorkflowDefinitionsResponse.from_dict(workflow_definitions_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


