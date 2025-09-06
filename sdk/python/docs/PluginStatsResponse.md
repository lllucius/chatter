# PluginStatsResponse

Response schema for plugin statistics.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_plugins** | **int** | Total number of plugins | 
**active_plugins** | **int** | Number of active plugins | 
**inactive_plugins** | **int** | Number of inactive plugins | 
**plugin_types** | **Dict[str, int]** | Plugin count by type | 
**plugins_directory** | **str** | Plugin installation directory | 

## Example

```python
from chatter_sdk.models.plugin_stats_response import PluginStatsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PluginStatsResponse from a JSON string
plugin_stats_response_instance = PluginStatsResponse.from_json(json)
# print the JSON string representation of the object
print(PluginStatsResponse.to_json())

# convert the object into a dict
plugin_stats_response_dict = plugin_stats_response_instance.to_dict()
# create an instance of PluginStatsResponse from a dict
plugin_stats_response_from_dict = PluginStatsResponse.from_dict(plugin_stats_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


