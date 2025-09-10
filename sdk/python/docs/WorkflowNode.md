# WorkflowNode

Schema for a workflow node.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Unique node identifier | 
**type** | **str** | Node type | 
**position** | **Dict[str, float]** | Node position (x, y) | 
**data** | [**WorkflowNodeData**](WorkflowNodeData.md) |  | 
**selected** | **bool** |  | [optional] 
**dragging** | **bool** |  | [optional] 

## Example

```python
from chatter_sdk.models.workflow_node import WorkflowNode

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowNode from a JSON string
workflow_node_instance = WorkflowNode.from_json(json)
# print the JSON string representation of the object
print(WorkflowNode.to_json())

# convert the object into a dict
workflow_node_dict = workflow_node_instance.to_dict()
# create an instance of WorkflowNode from a dict
workflow_node_from_dict = WorkflowNode.from_dict(workflow_node_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


