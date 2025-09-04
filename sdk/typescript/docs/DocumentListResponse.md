# DocumentListResponse

Schema for document list response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**documents** | [**Array&lt;DocumentResponse&gt;**](DocumentResponse.md) | List of documents | [default to undefined]
**total_count** | **number** | Total number of documents | [default to undefined]
**limit** | **number** | Applied limit | [default to undefined]
**offset** | **number** | Applied offset | [default to undefined]

## Example

```typescript
import { DocumentListResponse } from 'chatter-sdk';

const instance: DocumentListResponse = {
    documents,
    total_count,
    limit,
    offset,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
