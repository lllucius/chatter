# JobResponse

Response schema for job data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **string** | Job ID | [default to undefined]
**name** | **string** | Job name | [default to undefined]
**function_name** | **string** | Function name | [default to undefined]
**priority** | [**JobPriority**](JobPriority.md) | Job priority | [default to undefined]
**status** | [**JobStatus**](JobStatus.md) | Job status | [default to undefined]
**created_at** | **string** | Creation timestamp | [default to undefined]
**started_at** | **string** |  | [optional] [default to undefined]
**completed_at** | **string** |  | [optional] [default to undefined]
**scheduled_at** | **string** |  | [optional] [default to undefined]
**retry_count** | **number** | Number of retry attempts | [default to undefined]
**max_retries** | **number** | Maximum retry attempts | [default to undefined]
**error_message** | **string** |  | [optional] [default to undefined]
**result** | [****](.md) | Job result if completed | [optional] [default to undefined]
**progress** | **number** | Job progress percentage | [optional] [default to 0]
**progress_message** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { JobResponse } from 'chatter-sdk';

const instance: JobResponse = {
    id,
    name,
    function_name,
    priority,
    status,
    created_at,
    started_at,
    completed_at,
    scheduled_at,
    retry_count,
    max_retries,
    error_message,
    result,
    progress,
    progress_message,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
