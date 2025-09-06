# McpStatusResponse

Schema for MCP status response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | MCP service status | 
**servers** | **List[Dict[str, object]]** | Connected servers | 
**last_check** | **datetime** |  | [optional] 
**errors** | **List[str]** | Any error messages | [optional] 

## Example

```python
from chatter_sdk.models.mcp_status_response import McpStatusResponse

# TODO update the JSON string below
json = "{}"
# create an instance of McpStatusResponse from a JSON string
mcp_status_response_instance = McpStatusResponse.from_json(json)
# print the JSON string representation of the object
print(McpStatusResponse.to_json())

# convert the object into a dict
mcp_status_response_dict = mcp_status_response_instance.to_dict()
# create an instance of McpStatusResponse from a dict
mcp_status_response_from_dict = McpStatusResponse.from_dict(mcp_status_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


