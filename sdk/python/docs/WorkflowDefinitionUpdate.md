# WorkflowDefinitionUpdate

Schema for updating a workflow definition.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**nodes** | [**List[WorkflowNode]**](WorkflowNode.md) |  | [optional] 
**edges** | [**List[WorkflowEdge]**](WorkflowEdge.md) |  | [optional] 
**metadata** | **Dict[str, object]** |  | [optional] 

## Example

```python
from chatter_sdk.models.workflow_definition_update import WorkflowDefinitionUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowDefinitionUpdate from a JSON string
workflow_definition_update_instance = WorkflowDefinitionUpdate.from_json(json)
# print the JSON string representation of the object
print(WorkflowDefinitionUpdate.to_json())

# convert the object into a dict
workflow_definition_update_dict = workflow_definition_update_instance.to_dict()
# create an instance of WorkflowDefinitionUpdate from a dict
workflow_definition_update_from_dict = WorkflowDefinitionUpdate.from_dict(workflow_definition_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


