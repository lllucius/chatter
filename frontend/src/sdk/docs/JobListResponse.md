# JobListResponse

Response schema for job list.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**jobs** | [**Array&lt;JobResponse&gt;**](JobResponse.md) | List of jobs | [default to undefined]
**total** | **number** | Total number of jobs | [default to undefined]

## Example

```typescript
import { JobListResponse } from 'chatter-sdk';

const instance: JobListResponse = {
    jobs,
    total,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
