# WorkflowNodeData

Schema for workflow node data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**label** | **str** | Node display label | 
**node_type** | **str** | Type of the node | 
**config** | **Dict[str, object]** |  | [optional] 

## Example

```python
from chatter_sdk.models.workflow_node_data import WorkflowNodeData

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowNodeData from a JSON string
workflow_node_data_instance = WorkflowNodeData.from_json(json)
# print the JSON string representation of the object
print(WorkflowNodeData.to_json())

# convert the object into a dict
workflow_node_data_dict = workflow_node_data_instance.to_dict()
# create an instance of WorkflowNodeData from a dict
workflow_node_data_from_dict = WorkflowNodeData.from_dict(workflow_node_data_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


