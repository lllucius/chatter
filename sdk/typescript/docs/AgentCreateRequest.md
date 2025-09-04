# AgentCreateRequest

Request schema for creating an agent.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | Agent name | [default to undefined]
**description** | **string** | Agent description | [default to undefined]
**agent_type** | [**AgentType**](AgentType.md) | Type of agent | [default to undefined]
**system_prompt** | **string** | System prompt for the agent | [default to undefined]
**personality_traits** | **Array&lt;string&gt;** | Agent personality traits | [optional] [default to undefined]
**knowledge_domains** | **Array&lt;string&gt;** | Knowledge domains | [optional] [default to undefined]
**response_style** | **string** | Response style | [optional] [default to 'professional']
**capabilities** | [**Array&lt;AgentCapability&gt;**](AgentCapability.md) | Agent capabilities | [optional] [default to undefined]
**available_tools** | **Array&lt;string&gt;** | Available tools | [optional] [default to undefined]
**primary_llm** | **string** | Primary LLM provider | [optional] [default to 'openai']
**fallback_llm** | **string** | Fallback LLM provider | [optional] [default to 'anthropic']
**temperature** | **number** | Temperature for responses | [optional] [default to 0.7]
**max_tokens** | **number** | Maximum tokens | [optional] [default to 4096]
**max_conversation_length** | **number** | Maximum conversation length | [optional] [default to 50]
**context_window_size** | **number** | Context window size | [optional] [default to 4000]
**response_timeout** | **number** | Response timeout in seconds | [optional] [default to 30]
**learning_enabled** | **boolean** | Enable learning from feedback | [optional] [default to true]
**feedback_weight** | **number** | Weight for feedback learning | [optional] [default to 0.1]
**adaptation_threshold** | **number** | Adaptation threshold | [optional] [default to 0.8]
**tags** | **Array&lt;string&gt;** | Agent tags | [optional] [default to undefined]
**metadata** | **{ [key: string]: any; }** | Additional metadata | [optional] [default to undefined]

## Example

```typescript
import { AgentCreateRequest } from 'chatter-sdk';

const instance: AgentCreateRequest = {
    name,
    description,
    agent_type,
    system_prompt,
    personality_traits,
    knowledge_domains,
    response_style,
    capabilities,
    available_tools,
    primary_llm,
    fallback_llm,
    temperature,
    max_tokens,
    max_conversation_length,
    context_window_size,
    response_timeout,
    learning_enabled,
    feedback_weight,
    adaptation_threshold,
    tags,
    metadata,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
