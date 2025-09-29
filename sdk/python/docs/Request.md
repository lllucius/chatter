# Request


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
from chatter_sdk.models.request import Request

# TODO update the JSON string below
json = "{}"
# create an instance of Request from a JSON string
request_instance = Request.from_json(json)
# print the JSON string representation of the object
print(Request.to_json())

# convert the object into a dict
request_dict = request_instance.to_dict()
# create an instance of Request from a dict
request_from_dict = Request.from_dict(request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


