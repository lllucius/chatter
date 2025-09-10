# WorkflowEdge

Schema for a workflow edge.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Unique edge identifier | 
**source** | **str** | Source node ID | 
**target** | **str** | Target node ID | 
**source_handle** | **str** |  | [optional] 
**target_handle** | **str** |  | [optional] 
**type** | **str** |  | [optional] 
**data** | [**WorkflowEdgeData**](WorkflowEdgeData.md) |  | [optional] 

## Example

```python
from chatter_sdk.models.workflow_edge import WorkflowEdge

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowEdge from a JSON string
workflow_edge_instance = WorkflowEdge.from_json(json)
# print the JSON string representation of the object
print(WorkflowEdge.to_json())

# convert the object into a dict
workflow_edge_dict = workflow_edge_instance.to_dict()
# create an instance of WorkflowEdge from a dict
workflow_edge_from_dict = WorkflowEdge.from_dict(workflow_edge_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


