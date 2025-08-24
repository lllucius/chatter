# DocumentChunkResponse

Schema for document chunk response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** | Chunk ID | [default to undefined]
**document_id** | **string** | Document ID | [default to undefined]
**content** | **string** | Chunk content | [default to undefined]
**chunk_index** | **number** | Chunk index | [default to undefined]
**start_char** | **number** |  | [optional] [default to undefined]
**end_char** | **number** |  | [optional] [default to undefined]
**extra_metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**token_count** | **number** |  | [optional] [default to undefined]
**language** | **string** |  | [optional] [default to undefined]
**embedding_model** | **string** |  | [optional] [default to undefined]
**embedding_provider** | **string** |  | [optional] [default to undefined]
**embedding_created_at** | **string** |  | [optional] [default to undefined]
**content_hash** | **string** | Content hash | [default to undefined]
**has_embedding** | **boolean** | Whether chunk has embedding | [default to undefined]
**created_at** | **string** | Creation time | [default to undefined]
**updated_at** | **string** | Last update time | [default to undefined]

## Example

```typescript
import { DocumentChunkResponse } from 'chatter-sdk';

const instance: DocumentChunkResponse = {
    id,
    document_id,
    content,
    chunk_index,
    start_char,
    end_char,
    extra_metadata,
    token_count,
    language,
    embedding_model,
    embedding_provider,
    embedding_created_at,
    content_hash,
    has_embedding,
    created_at,
    updated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
