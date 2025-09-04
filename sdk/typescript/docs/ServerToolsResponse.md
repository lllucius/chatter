# ServerToolsResponse

Schema for server tools response with pagination.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tools** | [**Array&lt;ServerToolResponse&gt;**](ServerToolResponse.md) | List of server tools | [default to undefined]
**total_count** | **number** | Total number of tools | [default to undefined]
**limit** | **number** | Applied limit | [default to undefined]
**offset** | **number** | Applied offset | [default to undefined]

## Example

```typescript
import { ServerToolsResponse } from 'chatter-sdk';

const instance: ServerToolsResponse = {
    tools,
    total_count,
    limit,
    offset,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
