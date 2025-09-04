# AgentUpdateRequest

Request schema for updating an agent.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**system_prompt** | **string** |  | [optional] [default to undefined]
**status** | [**AgentStatus**](AgentStatus.md) |  | [optional] [default to undefined]
**personality_traits** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**knowledge_domains** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**response_style** | **string** |  | [optional] [default to undefined]
**capabilities** | [**Array&lt;AgentCapability&gt;**](AgentCapability.md) |  | [optional] [default to undefined]
**available_tools** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**primary_llm** | **string** |  | [optional] [default to undefined]
**fallback_llm** | **string** |  | [optional] [default to undefined]
**temperature** | **number** |  | [optional] [default to undefined]
**max_tokens** | **number** |  | [optional] [default to undefined]
**max_conversation_length** | **number** |  | [optional] [default to undefined]
**context_window_size** | **number** |  | [optional] [default to undefined]
**response_timeout** | **number** |  | [optional] [default to undefined]
**learning_enabled** | **boolean** |  | [optional] [default to undefined]
**feedback_weight** | **number** |  | [optional] [default to undefined]
**adaptation_threshold** | **number** |  | [optional] [default to undefined]
**tags** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]

## Example

```typescript
import { AgentUpdateRequest } from 'chatter-sdk';

const instance: AgentUpdateRequest = {
    name,
    description,
    system_prompt,
    status,
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
