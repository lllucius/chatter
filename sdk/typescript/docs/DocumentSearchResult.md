# DocumentSearchResult

Schema for document search result.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **string** | Document ID | [default to undefined]
**chunk_id** | **string** | Chunk ID | [default to undefined]
**score** | **number** | Similarity score | [default to undefined]
**content** | **string** | Matching content | [default to undefined]
**metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**document** | [**DocumentResponse**](DocumentResponse.md) | Document information | [default to undefined]

## Example

```typescript
import { DocumentSearchResult } from 'chatter-sdk';

const instance: DocumentSearchResult = {
    document_id,
    chunk_id,
    score,
    content,
    metadata,
    document,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
