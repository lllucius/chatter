# PluginUpdateRequest

Request schema for updating a plugin.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **bool** |  | [optional] 
**configuration** | **Dict[str, object]** |  | [optional] 

## Example

```python
from chatter_sdk.models.plugin_update_request import PluginUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PluginUpdateRequest from a JSON string
plugin_update_request_instance = PluginUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(PluginUpdateRequest.to_json())

# convert the object into a dict
plugin_update_request_dict = plugin_update_request_instance.to_dict()
# create an instance of PluginUpdateRequest from a dict
plugin_update_request_from_dict = PluginUpdateRequest.from_dict(plugin_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


