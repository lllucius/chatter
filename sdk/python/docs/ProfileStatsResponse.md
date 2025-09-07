# ProfileStatsResponse

Schema for profile statistics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_profiles** | **int** | Total number of profiles | 
**profiles_by_type** | **Dict[str, int]** | Profiles grouped by type | 
**profiles_by_provider** | **Dict[str, int]** | Profiles grouped by LLM provider | 
**most_used_profiles** | [**List[ProfileResponse]**](ProfileResponse.md) | Most frequently used profiles | 
**recent_profiles** | [**List[ProfileResponse]**](ProfileResponse.md) | Recently created profiles | 
**usage_stats** | **Dict[str, object]** | Usage statistics | 

## Example

```python
from chatter_sdk.models.profile_stats_response import ProfileStatsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ProfileStatsResponse from a JSON string
profile_stats_response_instance = ProfileStatsResponse.from_json(json)
# print the JSON string representation of the object
print(ProfileStatsResponse.to_json())

# convert the object into a dict
profile_stats_response_dict = profile_stats_response_instance.to_dict()
# create an instance of ProfileStatsResponse from a dict
profile_stats_response_from_dict = ProfileStatsResponse.from_dict(profile_stats_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


