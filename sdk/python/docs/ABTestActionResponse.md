# ABTestActionResponse

Response schema for test actions (start, pause, complete).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether action was successful | 
**message** | **str** | Action result message | 
**test_id** | **str** | Test ID | 
**new_status** | [**TestStatus**](TestStatus.md) |  | 

## Example

```python
from chatter_sdk.models.ab_test_action_response import ABTestActionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ABTestActionResponse from a JSON string
ab_test_action_response_instance = ABTestActionResponse.from_json(json)
# print the JSON string representation of the object
print(ABTestActionResponse.to_json())

# convert the object into a dict
ab_test_action_response_dict = ab_test_action_response_instance.to_dict()
# create an instance of ABTestActionResponse from a dict
ab_test_action_response_from_dict = ABTestActionResponse.from_dict(ab_test_action_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


