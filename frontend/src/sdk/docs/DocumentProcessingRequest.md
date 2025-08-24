# DocumentProcessingRequest

Schema for document processing request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**reprocess** | **boolean** | Force reprocessing | [optional] [default to false]
**chunk_size** | **number** |  | [optional] [default to undefined]
**chunk_overlap** | **number** |  | [optional] [default to undefined]
**generate_embeddings** | **boolean** | Generate embeddings for chunks | [optional] [default to true]

## Example

```typescript
import { DocumentProcessingRequest } from 'chatter-sdk';

const instance: DocumentProcessingRequest = {
    reprocess,
    chunk_size,
    chunk_overlap,
    generate_embeddings,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
