# ProfileCloneRequest

Schema for profile clone request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | New profile name | 
**description** | **str** |  | [optional] 
**modifications** | [**ProfileUpdate**](ProfileUpdate.md) |  | [optional] 

## Example

```python
from chatter_sdk.models.profile_clone_request import ProfileCloneRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ProfileCloneRequest from a JSON string
profile_clone_request_instance = ProfileCloneRequest.from_json(json)
# print the JSON string representation of the object
print(ProfileCloneRequest.to_json())

# convert the object into a dict
profile_clone_request_dict = profile_clone_request_instance.to_dict()
# create an instance of ProfileCloneRequest from a dict
profile_clone_request_from_dict = ProfileCloneRequest.from_dict(profile_clone_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


