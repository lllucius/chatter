# ABTestListResponse

Response schema for A/B test list.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**tests** | [**List[ABTestResponse]**](ABTestResponse.md) | List of tests | 
**total** | **int** | Total number of tests | 

## Example

```python
from chatter_sdk.models.ab_test_list_response import ABTestListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ABTestListResponse from a JSON string
ab_test_list_response_instance = ABTestListResponse.from_json(json)
# print the JSON string representation of the object
print(ABTestListResponse.to_json())

# convert the object into a dict
ab_test_list_response_dict = ab_test_list_response_instance.to_dict()
# create an instance of ABTestListResponse from a dict
ab_test_list_response_from_dict = ABTestListResponse.from_dict(ab_test_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


