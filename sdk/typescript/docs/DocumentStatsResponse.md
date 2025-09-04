# DocumentStatsResponse

Schema for document statistics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_documents** | **number** | Total number of documents | [default to undefined]
**total_chunks** | **number** | Total number of chunks | [default to undefined]
**total_size_bytes** | **number** | Total size in bytes | [default to undefined]
**documents_by_status** | **{ [key: string]: number; }** | Documents grouped by status | [default to undefined]
**documents_by_type** | **{ [key: string]: number; }** | Documents grouped by type | [default to undefined]
**processing_stats** | **{ [key: string]: any; }** | Processing statistics | [default to undefined]

## Example

```typescript
import { DocumentStatsResponse } from 'chatter-sdk';

const instance: DocumentStatsResponse = {
    total_documents,
    total_chunks,
    total_size_bytes,
    documents_by_status,
    documents_by_type,
    processing_stats,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
