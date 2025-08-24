# AgentCapability

Agent capability definition.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [default to undefined]
**description** | **string** |  | [default to undefined]
**required_tools** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**required_models** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**confidence_threshold** | **number** |  | [optional] [default to 0.7]
**enabled** | **boolean** |  | [optional] [default to true]

## Example

```typescript
import { AgentCapability } from 'chatter-sdk';

const instance: AgentCapability = {
    name,
    description,
    required_tools,
    required_models,
    confidence_threshold,
    enabled,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
