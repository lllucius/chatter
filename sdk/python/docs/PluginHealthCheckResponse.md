# PluginHealthCheckResponse

Response schema for plugin health check.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**summary** | **Dict[str, object]** | Health check summary | 
**results** | **Dict[str, Dict[str, object]]** | Detailed health check results for each plugin | 

## Example

```python
from chatter_sdk.models.plugin_health_check_response import PluginHealthCheckResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PluginHealthCheckResponse from a JSON string
plugin_health_check_response_instance = PluginHealthCheckResponse.from_json(json)
# print the JSON string representation of the object
print(PluginHealthCheckResponse.to_json())

# convert the object into a dict
plugin_health_check_response_dict = plugin_health_check_response_instance.to_dict()
# create an instance of PluginHealthCheckResponse from a dict
plugin_health_check_response_from_dict = PluginHealthCheckResponse.from_dict(plugin_health_check_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


