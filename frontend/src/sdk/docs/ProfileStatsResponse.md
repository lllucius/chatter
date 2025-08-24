# ProfileStatsResponse

Schema for profile statistics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_profiles** | **number** | Total number of profiles | [default to undefined]
**profiles_by_type** | **{ [key: string]: number; }** | Profiles grouped by type | [default to undefined]
**profiles_by_provider** | **{ [key: string]: number; }** | Profiles grouped by LLM provider | [default to undefined]
**most_used_profiles** | [**Array&lt;ProfileResponse&gt;**](ProfileResponse.md) | Most frequently used profiles | [default to undefined]
**recent_profiles** | [**Array&lt;ProfileResponse&gt;**](ProfileResponse.md) | Recently created profiles | [default to undefined]
**usage_stats** | **{ [key: string]: any; }** | Usage statistics | [default to undefined]

## Example

```typescript
import { ProfileStatsResponse } from 'chatter-sdk';

const instance: ProfileStatsResponse = {
    total_profiles,
    profiles_by_type,
    profiles_by_provider,
    most_used_profiles,
    recent_profiles,
    usage_stats,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
