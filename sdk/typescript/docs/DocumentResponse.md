# DocumentResponse

Schema for document response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **string** |  | [optional] [default to undefined]
**description** | **string** |  | [optional] [default to undefined]
**tags** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**extra_metadata** | **{ [key: string]: any; }** |  | [optional] [default to undefined]
**is_public** | **boolean** | Whether document is public | [optional] [default to false]
**id** | **string** | Document ID | [default to undefined]
**owner_id** | **string** | Owner user ID | [default to undefined]
**filename** | **string** | Document filename | [default to undefined]
**original_filename** | **string** | Original filename | [default to undefined]
**file_size** | **number** | File size in bytes | [default to undefined]
**file_hash** | **string** | File hash (SHA-256) | [default to undefined]
**mime_type** | **string** | MIME type | [default to undefined]
**document_type** | [**DocumentType**](DocumentType.md) | Document type | [default to undefined]
**status** | [**DocumentStatus**](DocumentStatus.md) | Processing status | [default to undefined]
**processing_started_at** | **string** |  | [optional] [default to undefined]
**processing_completed_at** | **string** |  | [optional] [default to undefined]
**processing_error** | **string** |  | [optional] [default to undefined]
**chunk_size** | **number** | Chunk size | [default to undefined]
**chunk_overlap** | **number** | Chunk overlap | [default to undefined]
**chunk_count** | **number** | Number of chunks | [default to undefined]
**version** | **number** | Document version | [default to undefined]
**parent_document_id** | **string** |  | [optional] [default to undefined]
**view_count** | **number** | View count | [default to undefined]
**search_count** | **number** | Search count | [default to undefined]
**last_accessed_at** | **string** |  | [optional] [default to undefined]
**created_at** | **string** | Creation time | [default to undefined]
**updated_at** | **string** | Last update time | [default to undefined]

## Example

```typescript
import { DocumentResponse } from 'chatter-sdk';

const instance: DocumentResponse = {
    title,
    description,
    tags,
    extra_metadata,
    is_public,
    id,
    owner_id,
    filename,
    original_filename,
    file_size,
    file_hash,
    mime_type,
    document_type,
    status,
    processing_started_at,
    processing_completed_at,
    processing_error,
    chunk_size,
    chunk_overlap,
    chunk_count,
    version,
    parent_document_id,
    view_count,
    search_count,
    last_accessed_at,
    created_at,
    updated_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
