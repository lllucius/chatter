# DocumentSearchRequest

Schema for document search request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**query** | **string** | Search query | [default to undefined]
**limit** | **number** | Maximum number of results | [optional] [default to 10]
**score_threshold** | **number** | Minimum similarity score | [optional] [default to 0.5]
**document_types** | [**Array&lt;DocumentType&gt;**](DocumentType.md) |  | [optional] [default to undefined]
**tags** | **Array&lt;string&gt;** |  | [optional] [default to undefined]
**include_content** | **boolean** | Include document content in results | [optional] [default to false]

## Example

```typescript
import { DocumentSearchRequest } from 'chatter-sdk';

const instance: DocumentSearchRequest = {
    query,
    limit,
    score_threshold,
    document_types,
    tags,
    include_content,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
