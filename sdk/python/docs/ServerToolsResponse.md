# ServerToolsResponse

Schema for server tools response with pagination.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tools** | [**List[ServerToolResponse]**](ServerToolResponse.md) | List of server tools | 
**total_count** | **int** | Total number of tools | 
**limit** | **int** | Applied limit | 
**offset** | **int** | Applied offset | 

## Example

```python
from chatter_sdk.models.server_tools_response import ServerToolsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ServerToolsResponse from a JSON string
server_tools_response_instance = ServerToolsResponse.from_json(json)
# print the JSON string representation of the object
print(ServerToolsResponse.to_json())

# convert the object into a dict
server_tools_response_dict = server_tools_response_instance.to_dict()
# create an instance of ServerToolsResponse from a dict
server_tools_response_from_dict = ServerToolsResponse.from_dict(server_tools_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


