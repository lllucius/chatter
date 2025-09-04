# JobStatsResponse

Response schema for job statistics.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_jobs** | **number** | Total number of jobs | [default to undefined]
**pending_jobs** | **number** | Number of pending jobs | [default to undefined]
**running_jobs** | **number** | Number of running jobs | [default to undefined]
**completed_jobs** | **number** | Number of completed jobs | [default to undefined]
**failed_jobs** | **number** | Number of failed jobs | [default to undefined]
**queue_size** | **number** | Current queue size | [default to undefined]
**active_workers** | **number** | Number of active workers | [default to undefined]

## Example

```typescript
import { JobStatsResponse } from 'chatter-sdk';

const instance: JobStatsResponse = {
    total_jobs,
    pending_jobs,
    running_jobs,
    completed_jobs,
    failed_jobs,
    queue_size,
    active_workers,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
