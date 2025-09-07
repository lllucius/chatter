# PluginResponse

Response schema for plugin data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Plugin ID | 
**name** | **str** | Plugin name | 
**version** | **str** | Plugin version | 
**description** | **str** | Plugin description | 
**author** | **str** | Plugin author | 
**plugin_type** | [**PluginType**](PluginType.md) |  | 
**status** | [**PluginStatus**](PluginStatus.md) |  | 
**entry_point** | **str** | Plugin entry point | 
**capabilities** | **List[Dict[str, object]]** | Plugin capabilities | 
**dependencies** | **List[str]** | Plugin dependencies | 
**permissions** | **List[str]** | Required permissions | 
**enabled** | **bool** | Whether plugin is enabled | 
**error_message** | **str** |  | [optional] 
**installed_at** | **datetime** | Installation timestamp | 
**updated_at** | **datetime** | Last update timestamp | 
**metadata** | **Dict[str, object]** | Additional metadata | 

## Example

```python
from chatter_sdk.models.plugin_response import PluginResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PluginResponse from a JSON string
plugin_response_instance = PluginResponse.from_json(json)
# print the JSON string representation of the object
print(PluginResponse.to_json())

# convert the object into a dict
plugin_response_dict = plugin_response_instance.to_dict()
# create an instance of PluginResponse from a dict
plugin_response_from_dict = PluginResponse.from_dict(plugin_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


