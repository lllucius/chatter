# AgentResponse

Response schema for agent data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** | Agent ID | [default to undefined]
**name** | **string** | Agent name | [default to undefined]
**description** | **string** | Agent description | [default to undefined]
**type** | [**AgentType**](AgentType.md) | Type of agent | [default to undefined]
**status** | [**AgentStatus**](AgentStatus.md) | Agent status | [default to undefined]
**system_message** | **string** | System message | [default to undefined]
**personality_traits** | **Array&lt;string&gt;** | Agent personality traits | [default to undefined]
**knowledge_domains** | **Array&lt;string&gt;** | Knowledge domains | [default to undefined]
**response_style** | **string** | Response style | [default to undefined]
**capabilities** | [**Array&lt;AgentCapability&gt;**](AgentCapability.md) | Agent capabilities | [default to undefined]
**available_tools** | **Array&lt;string&gt;** | Available tools | [default to undefined]
**primary_llm** | **string** | Primary LLM provider | [default to undefined]
**fallback_llm** | **string** | Fallback LLM provider | [default to undefined]
**temperature** | **number** | Temperature for responses | [default to undefined]
**max_tokens** | **number** | Maximum tokens | [default to undefined]
**max_conversation_length** | **number** | Maximum conversation length | [default to undefined]
**context_window_size** | **number** | Context window size | [default to undefined]
**response_timeout** | **number** | Response timeout in seconds | [default to undefined]
**learning_enabled** | **boolean** | Learning enabled | [default to undefined]
**feedback_weight** | **number** | Feedback weight | [default to undefined]
**adaptation_threshold** | **number** | Adaptation threshold | [default to undefined]
**created_at** | **string** | Creation timestamp | [default to undefined]
**updated_at** | **string** | Last update timestamp | [default to undefined]
**created_by** | **string** | Creator | [default to undefined]
**tags** | **Array&lt;string&gt;** | Agent tags | [default to undefined]
**metadata** | **{ [key: string]: any; }** | Additional metadata | [default to undefined]

## Example

```typescript
import { AgentResponse } from 'chatter-sdk';

const instance: AgentResponse = {
    id,
    name,
    description,
    type,
    status,
    system_message,
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
    created_at,
    updated_at,
    created_by,
    tags,
    metadata,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
