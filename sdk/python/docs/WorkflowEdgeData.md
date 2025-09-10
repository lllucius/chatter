# WorkflowEdgeData

Schema for workflow edge data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**condition** | **str** |  | [optional] 
**label** | **str** |  | [optional] 

## Example

```python
from chatter_sdk.models.workflow_edge_data import WorkflowEdgeData

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowEdgeData from a JSON string
workflow_edge_data_instance = WorkflowEdgeData.from_json(json)
# print the JSON string representation of the object
print(WorkflowEdgeData.to_json())

# convert the object into a dict
workflow_edge_data_dict = workflow_edge_data_instance.to_dict()
# create an instance of WorkflowEdgeData from a dict
workflow_edge_data_from_dict = WorkflowEdgeData.from_dict(workflow_edge_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


