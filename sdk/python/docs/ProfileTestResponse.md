# ProfileTestResponse

Schema for profile test response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**profile_id** | **str** | Profile ID | 
**test_message** | **str** | Test message sent | 
**response** | **str** | Generated response | 
**usage_info** | **Dict[str, object]** | Token usage and cost information | 
**response_time_ms** | **int** | Response time in milliseconds | 
**retrieval_results** | **List[Dict[str, object]]** |  | [optional] 
**tools_used** | **List[str]** |  | [optional] 

## Example

```python
from chatter_sdk.models.profile_test_response import ProfileTestResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ProfileTestResponse from a JSON string
profile_test_response_instance = ProfileTestResponse.from_json(json)
# print the JSON string representation of the object
print(ProfileTestResponse.to_json())

# convert the object into a dict
profile_test_response_dict = profile_test_response_instance.to_dict()
# create an instance of ProfileTestResponse from a dict
profile_test_response_from_dict = ProfileTestResponse.from_dict(profile_test_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


