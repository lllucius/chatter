# ProfileTestResponse

Schema for profile test response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**profile_id** | **string** | Profile ID | [default to undefined]
**test_message** | **string** | Test message sent | [default to undefined]
**response** | **string** | Generated response | [default to undefined]
**usage_info** | **{ [key: string]: any; }** | Token usage and cost information | [default to undefined]
**response_time_ms** | **number** | Response time in milliseconds | [default to undefined]
**retrieval_results** | **Array&lt;{ [key: string]: any; } | null&gt;** |  | [optional] [default to undefined]
**tools_used** | **Array&lt;string&gt;** |  | [optional] [default to undefined]

## Example

```typescript
import { ProfileTestResponse } from 'chatter-sdk';

const instance: ProfileTestResponse = {
    profile_id,
    test_message,
    response,
    usage_info,
    response_time_ms,
    retrieval_results,
    tools_used,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
