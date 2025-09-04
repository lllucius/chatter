# PaginationRequest

Common pagination request schema.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**limit** | **number** | Maximum number of results | [optional] [default to 50]
**offset** | **number** | Number of results to skip | [optional] [default to 0]

## Example

```typescript
import { PaginationRequest } from 'chatter-sdk';

const instance: PaginationRequest = {
    limit,
    offset,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
