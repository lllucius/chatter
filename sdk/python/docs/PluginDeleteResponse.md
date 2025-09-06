# PluginDeleteResponse

Response schema for plugin deletion.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether deletion was successful | 
**message** | **str** | Deletion result message | 

## Example

```python
from chatter_sdk.models.plugin_delete_response import PluginDeleteResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PluginDeleteResponse from a JSON string
plugin_delete_response_instance = PluginDeleteResponse.from_json(json)
# print the JSON string representation of the object
print(PluginDeleteResponse.to_json())

# convert the object into a dict
plugin_delete_response_dict = plugin_delete_response_instance.to_dict()
# create an instance of PluginDeleteResponse from a dict
plugin_delete_response_from_dict = PluginDeleteResponse.from_dict(plugin_delete_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


