# DocumentProcessingResponse

Schema for document processing response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **string** | Document ID | [default to undefined]
**status** | [**DocumentStatus**](DocumentStatus.md) | Processing status | [default to undefined]
**message** | **string** | Status message | [default to undefined]
**processing_started_at** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { DocumentProcessingResponse } from 'chatter-sdk';

const instance: DocumentProcessingResponse = {
    document_id,
    status,
    message,
    processing_started_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
