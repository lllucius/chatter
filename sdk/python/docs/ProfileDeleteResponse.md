# ProfileDeleteResponse

Schema for profile delete response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Success message | 

## Example

```python
from chatter_sdk.models.profile_delete_response import ProfileDeleteResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ProfileDeleteResponse from a JSON string
profile_delete_response_instance = ProfileDeleteResponse.from_json(json)
# print the JSON string representation of the object
print(ProfileDeleteResponse.to_json())

# convert the object into a dict
profile_delete_response_dict = profile_delete_response_instance.to_dict()
# create an instance of ProfileDeleteResponse from a dict
profile_delete_response_from_dict = ProfileDeleteResponse.from_dict(profile_delete_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


