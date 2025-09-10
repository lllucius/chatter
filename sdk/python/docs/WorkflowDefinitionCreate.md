# WorkflowDefinitionCreate

Schema for creating a workflow definition.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Workflow name | 
**description** | **str** |  | [optional] 
**nodes** | [**List[WorkflowNode]**](WorkflowNode.md) | Workflow nodes | 
**edges** | [**List[WorkflowEdge]**](WorkflowEdge.md) | Workflow edges | 
**metadata** | **Dict[str, object]** |  | [optional] 
**is_public** | **bool** | Whether workflow is publicly visible | [optional] [default to False]
**tags** | **List[str]** |  | [optional] 
**template_id** | **str** |  | [optional] 

## Example

```python
from chatter_sdk.models.workflow_definition_create import WorkflowDefinitionCreate

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowDefinitionCreate from a JSON string
workflow_definition_create_instance = WorkflowDefinitionCreate.from_json(json)
# print the JSON string representation of the object
print(WorkflowDefinitionCreate.to_json())

# convert the object into a dict
workflow_definition_create_dict = workflow_definition_create_instance.to_dict()
# create an instance of WorkflowDefinitionCreate from a dict
workflow_definition_create_from_dict = WorkflowDefinitionCreate.from_dict(workflow_definition_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


