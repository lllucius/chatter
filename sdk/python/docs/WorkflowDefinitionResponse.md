# WorkflowDefinitionResponse

Schema for workflow definition response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Workflow name | 
**description** | **str** |  | [optional] 
**nodes** | [**List[WorkflowNode]**](WorkflowNode.md) | Workflow nodes | 
**edges** | [**List[WorkflowEdge]**](WorkflowEdge.md) | Workflow edges | 
**metadata** | **Dict[str, object]** |  | [optional] 
**is_public** | **bool** | Whether workflow is public | [optional] [default to False]
**tags** | **List[str]** |  | [optional] 
**template_id** | **str** |  | [optional] 
**id** | **str** | Unique node identifier | 
**owner_id** | **str** | Owner user ID | 
**version** | **int** | Workflow version | [optional] [default to 1]

## Example

```python
from chatter_sdk.models.workflow_definition_response import WorkflowDefinitionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowDefinitionResponse from a JSON string
workflow_definition_response_instance = WorkflowDefinitionResponse.from_json(json)
# print the JSON string representation of the object
print(WorkflowDefinitionResponse.to_json())

# convert the object into a dict
workflow_definition_response_dict = workflow_definition_response_instance.to_dict()
# create an instance of WorkflowDefinitionResponse from a dict
workflow_definition_response_from_dict = WorkflowDefinitionResponse.from_dict(workflow_definition_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


