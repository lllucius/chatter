# AgentResponse

Response schema for agent data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Agent ID | 
**name** | **str** | Agent name | 
**description** | **str** | Agent description | 
**type** | [**AgentType**](AgentType.md) |  | 
**status** | [**AgentStatus**](AgentStatus.md) |  | 
**system_message** | **str** | System message | 
**personality_traits** | **List[str]** | Agent personality traits | 
**knowledge_domains** | **List[str]** | Knowledge domains | 
**response_style** | **str** | Response style | 
**capabilities** | [**List[AgentCapability]**](AgentCapability.md) | Agent capabilities | 
**available_tools** | **List[str]** | Available tools | 
**primary_llm** | **str** | Primary LLM provider | 
**fallback_llm** | **str** | Fallback LLM provider | 
**temperature** | **float** | Temperature for responses | 
**max_tokens** | **int** | Maximum tokens | 
**max_conversation_length** | **int** | Maximum conversation length | 
**context_window_size** | **int** | Context window size | 
**response_timeout** | **int** | Response timeout in seconds | 
**learning_enabled** | **bool** | Learning enabled | 
**feedback_weight** | **float** | Feedback weight | 
**adaptation_threshold** | **float** | Adaptation threshold | 
**created_at** | **datetime** | Creation timestamp | 
**updated_at** | **datetime** | Last update timestamp | 
**created_by** | **str** | Creator | 
**tags** | **List[str]** | Agent tags | 
**metadata** | **Dict[str, object]** | Additional metadata | 

## Example

```python
from chatter_sdk.models.agent_response import AgentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AgentResponse from a JSON string
agent_response_instance = AgentResponse.from_json(json)
# print the JSON string representation of the object
print(AgentResponse.to_json())

# convert the object into a dict
agent_response_dict = agent_response_instance.to_dict()
# create an instance of AgentResponse from a dict
agent_response_from_dict = AgentResponse.from_dict(agent_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


