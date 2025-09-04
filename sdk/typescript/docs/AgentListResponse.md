# AgentListResponse

Response schema for agent list.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**agents** | [**Array&lt;AgentResponse&gt;**](AgentResponse.md) | List of agents | [default to undefined]
**total** | **number** | Total number of agents | [default to undefined]
**page** | **number** | Current page number | [default to undefined]
**per_page** | **number** | Number of items per page | [default to undefined]
**total_pages** | **number** | Total number of pages | [default to undefined]

## Example

```typescript
import { AgentListResponse } from 'chatter-sdk';

const instance: AgentListResponse = {
    agents,
    total,
    page,
    per_page,
    total_pages,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
