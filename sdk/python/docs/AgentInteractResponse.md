# AgentInteractResponse

Response schema for agent interaction.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**agent_id** | **str** | Agent ID | 
**response** | **str** | Agent response | 
**conversation_id** | **str** | Conversation ID | 
**tools_used** | **List[str]** | Tools used in response | 
**confidence_score** | **float** | Confidence score | 
**response_time** | **float** | Response time in seconds | 
**timestamp** | **datetime** | Response timestamp | 

## Example

```python
from chatter_sdk.models.agent_interact_response import AgentInteractResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AgentInteractResponse from a JSON string
agent_interact_response_instance = AgentInteractResponse.from_json(json)
# print the JSON string representation of the object
print(AgentInteractResponse.to_json())

# convert the object into a dict
agent_interact_response_dict = agent_interact_response_instance.to_dict()
# create an instance of AgentInteractResponse from a dict
agent_interact_response_from_dict = AgentInteractResponse.from_dict(agent_interact_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


