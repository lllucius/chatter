# AgentHealthResponse

Response schema for agent health check.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**agent_id** | **str** | Agent ID | 
**status** | [**AgentStatus**](AgentStatus.md) |  | 
**health** | **str** | Health status (healthy/unhealthy/unknown) | 
**last_interaction** | **datetime** |  | [optional] 
**response_time_avg** | **float** |  | [optional] 
**error_rate** | **float** |  | [optional] 

## Example

```python
from chatter_sdk.models.agent_health_response import AgentHealthResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AgentHealthResponse from a JSON string
agent_health_response_instance = AgentHealthResponse.from_json(json)
# print the JSON string representation of the object
print(AgentHealthResponse.to_json())

# convert the object into a dict
agent_health_response_dict = agent_health_response_instance.to_dict()
# create an instance of AgentHealthResponse from a dict
agent_health_response_from_dict = AgentHealthResponse.from_dict(agent_health_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


