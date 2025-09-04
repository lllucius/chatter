# ProfileListResponse

Schema for profile list response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**profiles** | [**Array&lt;ProfileResponse&gt;**](ProfileResponse.md) | List of profiles | [default to undefined]
**total_count** | **number** | Total number of profiles | [default to undefined]
**limit** | **number** | Applied limit | [default to undefined]
**offset** | **number** | Applied offset | [default to undefined]

## Example

```typescript
import { ProfileListResponse } from 'chatter-sdk';

const instance: ProfileListResponse = {
    profiles,
    total_count,
    limit,
    offset,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
