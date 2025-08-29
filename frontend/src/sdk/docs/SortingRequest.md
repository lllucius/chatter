# SortingRequest

Common sorting request schema.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sort_by** | **string** | Sort field | [optional] [default to 'created_at']
**sort_order** | **string** | Sort order | [optional] [default to 'desc']

## Example

```typescript
import { SortingRequest } from 'chatter-sdk';

const instance: SortingRequest = {
    sort_by,
    sort_order,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
