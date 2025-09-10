# NodeTypeResponse

Schema for node type information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** | Node type identifier | 
**name** | **str** | Human-readable name | 
**description** | **str** | Node description | 
**category** | **str** | Node category | 
**properties** | [**List[NodePropertyDefinition]**](NodePropertyDefinition.md) | Node properties | 
**icon** | **str** |  | [optional] 
**color** | **str** |  | [optional] 

## Example

```python
from chatter_sdk.models.node_type_response import NodeTypeResponse

# TODO update the JSON string below
json = "{}"
# create an instance of NodeTypeResponse from a JSON string
node_type_response_instance = NodeTypeResponse.from_json(json)
# print the JSON string representation of the object
print(NodeTypeResponse.to_json())

# convert the object into a dict
node_type_response_dict = node_type_response_instance.to_dict()
# create an instance of NodeTypeResponse from a dict
node_type_response_from_dict = NodeTypeResponse.from_dict(node_type_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


