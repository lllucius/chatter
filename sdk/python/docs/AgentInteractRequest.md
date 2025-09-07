# AgentInteractRequest

Request schema for interacting with an agent.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Message to send to the agent | 
**conversation_id** | **str** | Conversation ID | 
**context** | **Dict[str, object]** |  | [optional] 

## Example

```python
from chatter_sdk.models.agent_interact_request import AgentInteractRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AgentInteractRequest from a JSON string
agent_interact_request_instance = AgentInteractRequest.from_json(json)
# print the JSON string representation of the object
print(AgentInteractRequest.to_json())

# convert the object into a dict
agent_interact_request_dict = agent_interact_request_instance.to_dict()
# create an instance of AgentInteractRequest from a dict
agent_interact_request_from_dict = AgentInteractRequest.from_dict(agent_interact_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


