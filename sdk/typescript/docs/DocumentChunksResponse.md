# DocumentChunksResponse

Schema for document chunks response with pagination.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**chunks** | [**Array&lt;DocumentChunkResponse&gt;**](DocumentChunkResponse.md) | List of document chunks | [default to undefined]
**total_count** | **number** | Total number of chunks | [default to undefined]
**limit** | **number** | Applied limit | [default to undefined]
**offset** | **number** | Applied offset | [default to undefined]

## Example

```typescript
import { DocumentChunksResponse } from 'chatter-sdk';

const instance: DocumentChunksResponse = {
    chunks,
    total_count,
    limit,
    offset,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
