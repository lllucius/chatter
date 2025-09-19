# ToolConfig

Tool configuration for function calling workflows.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enabled** | **bool** | Enable tools | [optional] [default to True]
**allowed_tools** | **List[str]** |  | [optional] 
**max_tool_calls** | **int** | Max tool calls | [optional] [default to 5]
**parallel_tool_calls** | **bool** | Enable parallel tool calls | [optional] [default to False]
**tool_timeout_ms** | **int** | Tool timeout in ms | [optional] [default to 30000]

## Example

```python
from chatter_sdk.models.tool_config import ToolConfig

# TODO update the JSON string below
json = "{}"
# create an instance of ToolConfig from a JSON string
tool_config_instance = ToolConfig.from_json(json)
# print the JSON string representation of the object
print(ToolConfig.to_json())

# convert the object into a dict
tool_config_dict = tool_config_instance.to_dict()
# create an instance of ToolConfig from a dict
tool_config_from_dict = ToolConfig.from_dict(tool_config_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


