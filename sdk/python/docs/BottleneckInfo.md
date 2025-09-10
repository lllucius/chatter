# BottleneckInfo

Schema for bottleneck information.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**node_id** | **str** | Node ID with bottleneck | 
**node_type** | **str** | Node type | 
**reason** | **str** | Bottleneck reason | 
**severity** | **str** | Bottleneck severity (low/medium/high) | 
**suggestions** | **List[str]** | Optimization suggestions | 

## Example

```python
from chatter_sdk.models.bottleneck_info import BottleneckInfo

# TODO update the JSON string below
json = "{}"
# create an instance of BottleneckInfo from a JSON string
bottleneck_info_instance = BottleneckInfo.from_json(json)
# print the JSON string representation of the object
print(BottleneckInfo.to_json())

# convert the object into a dict
bottleneck_info_dict = bottleneck_info_instance.to_dict()
# create an instance of BottleneckInfo from a dict
bottleneck_info_from_dict = BottleneckInfo.from_dict(bottleneck_info_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


