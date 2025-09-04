# DocumentAnalyticsResponse

Schema for document analytics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_documents** | **number** | Total number of documents | [default to undefined]
**documents_by_status** | **{ [key: string]: number; }** | Documents by processing status | [default to undefined]
**documents_by_type** | **{ [key: string]: number; }** | Documents by file type | [default to undefined]
**avg_processing_time_seconds** | **number** | Average processing time | [default to undefined]
**processing_success_rate** | **number** | Processing success rate | [default to undefined]
**total_chunks** | **number** | Total number of chunks | [default to undefined]
**avg_chunks_per_document** | **number** | Average chunks per document | [default to undefined]
**total_storage_bytes** | **number** | Total storage used | [default to undefined]
**avg_document_size_bytes** | **number** | Average document size | [default to undefined]
**storage_by_type** | **{ [key: string]: number; }** | Storage usage by document type | [default to undefined]
**total_searches** | **number** | Total number of searches | [default to undefined]
**avg_search_results** | **number** | Average search results returned | [default to undefined]
**popular_search_terms** | **{ [key: string]: number; }** | Popular search terms | [default to undefined]
**total_views** | **number** | Total document views | [default to undefined]
**most_viewed_documents** | **Array&lt;{ [key: string]: any; } | null&gt;** | Most viewed documents | [default to undefined]
**documents_by_access_level** | **{ [key: string]: number; }** | Documents by access level | [default to undefined]

## Example

```typescript
import { DocumentAnalyticsResponse } from 'chatter-sdk';

const instance: DocumentAnalyticsResponse = {
    total_documents,
    documents_by_status,
    documents_by_type,
    avg_processing_time_seconds,
    processing_success_rate,
    total_chunks,
    avg_chunks_per_document,
    total_storage_bytes,
    avg_document_size_bytes,
    storage_by_type,
    total_searches,
    avg_search_results,
    popular_search_terms,
    total_views,
    most_viewed_documents,
    documents_by_access_level,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
