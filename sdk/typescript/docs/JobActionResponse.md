# JobActionResponse

Response schema for job actions.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **boolean** | Whether action was successful | [default to undefined]
**message** | **string** | Action result message | [default to undefined]
**job_id** | **string** | Job ID | [default to undefined]

## Example

```typescript
import { JobActionResponse } from 'chatter-sdk';

const instance: JobActionResponse = {
    success,
    message,
    job_id,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
