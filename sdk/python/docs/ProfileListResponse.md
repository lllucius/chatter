# ProfileListResponse

Schema for profile list response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**profiles** | [**List[ProfileResponse]**](ProfileResponse.md) | List of profiles | 
**total_count** | **int** | Total number of profiles | 
**limit** | **int** | Applied limit | 
**offset** | **int** | Applied offset | 

## Example

```python
from chatter_sdk.models.profile_list_response import ProfileListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ProfileListResponse from a JSON string
profile_list_response_instance = ProfileListResponse.from_json(json)
# print the JSON string representation of the object
print(ProfileListResponse.to_json())

# convert the object into a dict
profile_list_response_dict = profile_list_response_instance.to_dict()
# create an instance of ProfileListResponse from a dict
profile_list_response_from_dict = ProfileListResponse.from_dict(profile_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


