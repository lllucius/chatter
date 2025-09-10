# NodePropertyDefinition

Schema for node property definition.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Property name | 
**type** | **str** | Property type | 
**required** | **bool** | Whether property is required | [optional] [default to False]
**description** | **str** |  | [optional] 
**default_value** | [**AnyOf**](AnyOf.md) | Default value | [optional] 
**options** | **List[str]** |  | [optional] 
**min_value** | [**MinValue**](MinValue.md) |  | [optional] 
**max_value** | [**MaxValue**](MaxValue.md) |  | [optional] 

## Example

```python
from chatter_sdk.models.node_property_definition import NodePropertyDefinition

# TODO update the JSON string below
json = "{}"
# create an instance of NodePropertyDefinition from a JSON string
node_property_definition_instance = NodePropertyDefinition.from_json(json)
# print the JSON string representation of the object
print(NodePropertyDefinition.to_json())

# convert the object into a dict
node_property_definition_dict = node_property_definition_instance.to_dict()
# create an instance of NodePropertyDefinition from a dict
node_property_definition_from_dict = NodePropertyDefinition.from_dict(node_property_definition_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


