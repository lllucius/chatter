# PluginActionResponse

Response schema for plugin actions.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether action was successful | 
**message** | **str** | Action result message | 
**plugin_id** | **str** | Plugin ID | 

## Example

```python
from chatter_sdk.models.plugin_action_response import PluginActionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PluginActionResponse from a JSON string
plugin_action_response_instance = PluginActionResponse.from_json(json)
# print the JSON string representation of the object
print(PluginActionResponse.to_json())

# convert the object into a dict
plugin_action_response_dict = plugin_action_response_instance.to_dict()
# create an instance of PluginActionResponse from a dict
plugin_action_response_from_dict = PluginActionResponse.from_dict(plugin_action_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


