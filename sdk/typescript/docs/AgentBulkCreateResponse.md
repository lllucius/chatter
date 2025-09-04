# AgentBulkCreateResponse

Response schema for bulk agent creation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created** | [**Array&lt;AgentResponse&gt;**](AgentResponse.md) | Successfully created agents | [default to undefined]
**failed** | **Array&lt;{ [key: string]: any; } | null&gt;** | Failed agent creations with errors | [default to undefined]
**total_requested** | **number** | Total agents requested | [default to undefined]
**total_created** | **number** | Total agents successfully created | [default to undefined]

## Example

```typescript
import { AgentBulkCreateResponse } from 'chatter-sdk';

const instance: AgentBulkCreateResponse = {
    created,
    failed,
    total_requested,
    total_created,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
