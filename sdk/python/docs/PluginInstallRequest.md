# PluginInstallRequest

Request schema for installing a plugin.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**plugin_path** | **str** | Path to plugin file or directory | 
**enable_on_install** | **bool** | Enable plugin after installation | [optional] [default to True]

## Example

```python
from chatter_sdk.models.plugin_install_request import PluginInstallRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PluginInstallRequest from a JSON string
plugin_install_request_instance = PluginInstallRequest.from_json(json)
# print the JSON string representation of the object
print(PluginInstallRequest.to_json())

# convert the object into a dict
plugin_install_request_dict = plugin_install_request_instance.to_dict()
# create an instance of PluginInstallRequest from a dict
plugin_install_request_from_dict = PluginInstallRequest.from_dict(plugin_install_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


