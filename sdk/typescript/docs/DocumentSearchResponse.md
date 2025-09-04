# DocumentSearchResponse

Schema for document search response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**results** | [**Array&lt;DocumentSearchResult&gt;**](DocumentSearchResult.md) | Search results | [default to undefined]
**total_results** | **number** | Total number of matching results | [default to undefined]
**query** | **string** | Original search query | [default to undefined]
**score_threshold** | **number** | Applied score threshold | [default to undefined]

## Example

```typescript
import { DocumentSearchResponse } from 'chatter-sdk';

const instance: DocumentSearchResponse = {
    results,
    total_results,
    query,
    score_threshold,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
