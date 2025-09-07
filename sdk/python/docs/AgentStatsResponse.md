# AgentStatsResponse

Response schema for agent statistics.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_agents** | **int** | Total number of agents | 
**active_agents** | **int** | Number of active agents | 
**agent_types** | **Dict[str, int]** | Agents by type | 
**total_interactions** | **int** | Total interactions across all agents | 

## Example

```python
from chatter_sdk.models.agent_stats_response import AgentStatsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AgentStatsResponse from a JSON string
agent_stats_response_instance = AgentStatsResponse.from_json(json)
# print the JSON string representation of the object
print(AgentStatsResponse.to_json())

# convert the object into a dict
agent_stats_response_dict = agent_stats_response_instance.to_dict()
# create an instance of AgentStatsResponse from a dict
agent_stats_response_from_dict = AgentStatsResponse.from_dict(agent_stats_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


