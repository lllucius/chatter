# PluginListResponse

Response schema for plugin list.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**plugins** | [**List[PluginResponse]**](PluginResponse.md) | List of plugins | 
**total** | **int** | Total number of plugins | 

## Example

```python
from chatter_sdk.models.plugin_list_response import PluginListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PluginListResponse from a JSON string
plugin_list_response_instance = PluginListResponse.from_json(json)
# print the JSON string representation of the object
print(PluginListResponse.to_json())

# convert the object into a dict
plugin_list_response_dict = plugin_list_response_instance.to_dict()
# create an instance of PluginListResponse from a dict
plugin_list_response_from_dict = PluginListResponse.from_dict(plugin_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


