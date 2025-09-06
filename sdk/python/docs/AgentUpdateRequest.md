# AgentUpdateRequest

Request schema for updating an agent.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**system_prompt** | **str** |  | [optional] 
**status** | [**AgentStatus**](AgentStatus.md) |  | [optional] 
**personality_traits** | **List[str]** |  | [optional] 
**knowledge_domains** | **List[str]** |  | [optional] 
**response_style** | **str** |  | [optional] 
**capabilities** | [**List[AgentCapability]**](AgentCapability.md) |  | [optional] 
**available_tools** | **List[str]** |  | [optional] 
**primary_llm** | **str** |  | [optional] 
**fallback_llm** | **str** |  | [optional] 
**temperature** | **float** |  | [optional] 
**max_tokens** | **int** |  | [optional] 
**max_conversation_length** | **int** |  | [optional] 
**context_window_size** | **int** |  | [optional] 
**response_timeout** | **int** |  | [optional] 
**learning_enabled** | **bool** |  | [optional] 
**feedback_weight** | **float** |  | [optional] 
**adaptation_threshold** | **float** |  | [optional] 
**tags** | **List[str]** |  | [optional] 
**metadata** | **Dict[str, object]** |  | [optional] 

## Example

```python
from chatter_sdk.models.agent_update_request import AgentUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AgentUpdateRequest from a JSON string
agent_update_request_instance = AgentUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(AgentUpdateRequest.to_json())

# convert the object into a dict
agent_update_request_dict = agent_update_request_instance.to_dict()
# create an instance of AgentUpdateRequest from a dict
agent_update_request_from_dict = AgentUpdateRequest.from_dict(agent_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


