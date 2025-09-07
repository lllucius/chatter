# ProfileTestRequest

Schema for profile test request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test_message** | **str** | Test message | 
**include_retrieval** | **bool** | Include retrieval in test | [optional] [default to False]
**include_tools** | **bool** | Include tools in test | [optional] [default to False]

## Example

```python
from chatter_sdk.models.profile_test_request import ProfileTestRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ProfileTestRequest from a JSON string
profile_test_request_instance = ProfileTestRequest.from_json(json)
# print the JSON string representation of the object
print(ProfileTestRequest.to_json())

# convert the object into a dict
profile_test_request_dict = profile_test_request_instance.to_dict()
# create an instance of ProfileTestRequest from a dict
profile_test_request_from_dict = ProfileTestRequest.from_dict(profile_test_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


