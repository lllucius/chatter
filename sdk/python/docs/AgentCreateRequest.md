# AgentCreateRequest

Request schema for creating an agent.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Agent name | 
**description** | **str** | Agent description | 
**agent_type** | [**AgentType**](AgentType.md) |  | 
**system_prompt** | **str** | System prompt for the agent | 
**personality_traits** | **List[str]** | Agent personality traits | [optional] 
**knowledge_domains** | **List[str]** | Knowledge domains | [optional] 
**response_style** | **str** | Response style | [optional] [default to 'professional']
**capabilities** | [**List[AgentCapability]**](AgentCapability.md) | Agent capabilities | [optional] 
**available_tools** | **List[str]** | Available tools | [optional] 
**primary_llm** | **str** | Primary LLM provider | [optional] [default to 'openai']
**fallback_llm** | **str** | Fallback LLM provider | [optional] [default to 'anthropic']
**temperature** | **float** | Temperature for responses | [optional] [default to 0.7]
**max_tokens** | **int** | Maximum tokens | [optional] [default to 4096]
**max_conversation_length** | **int** | Maximum conversation length | [optional] [default to 50]
**context_window_size** | **int** | Context window size | [optional] [default to 4000]
**response_timeout** | **int** | Response timeout in seconds | [optional] [default to 30]
**learning_enabled** | **bool** | Enable learning from feedback | [optional] [default to True]
**feedback_weight** | **float** | Weight for feedback learning | [optional] [default to 0.1]
**adaptation_threshold** | **float** | Adaptation threshold | [optional] [default to 0.8]
**tags** | **List[str]** | Agent tags | [optional] 
**metadata** | **Dict[str, object]** | Additional metadata | [optional] 

## Example

```python
from chatter_sdk.models.agent_create_request import AgentCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AgentCreateRequest from a JSON string
agent_create_request_instance = AgentCreateRequest.from_json(json)
# print the JSON string representation of the object
print(AgentCreateRequest.to_json())

# convert the object into a dict
agent_create_request_dict = agent_create_request_instance.to_dict()
# create an instance of AgentCreateRequest from a dict
agent_create_request_from_dict = AgentCreateRequest.from_dict(agent_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


