# AgentDeleteResponse

Response schema for agent deletion.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether deletion was successful | 
**message** | **str** | Deletion result message | 

## Example

```python
from chatter_sdk.models.agent_delete_response import AgentDeleteResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AgentDeleteResponse from a JSON string
agent_delete_response_instance = AgentDeleteResponse.from_json(json)
# print the JSON string representation of the object
print(AgentDeleteResponse.to_json())

# convert the object into a dict
agent_delete_response_dict = agent_delete_response_instance.to_dict()
# create an instance of AgentDeleteResponse from a dict
agent_delete_response_from_dict = AgentDeleteResponse.from_dict(agent_delete_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


