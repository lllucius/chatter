# JobCreateRequest

Request schema for creating a job.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** | Job name | [default to undefined]
**function_name** | **string** | Function to execute | [default to undefined]
**args** | **Array&lt;any&gt;** | Function arguments | [optional] [default to undefined]
**kwargs** | **{ [key: string]: any; }** | Function keyword arguments | [optional] [default to undefined]
**priority** | [**JobPriority**](JobPriority.md) | Job priority | [optional] [default to undefined]
**max_retries** | **number** | Maximum retry attempts | [optional] [default to 3]
**schedule_at** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { JobCreateRequest } from 'chatter-sdk';

const instance: JobCreateRequest = {
    name,
    function_name,
    args,
    kwargs,
    priority,
    max_retries,
    schedule_at,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
