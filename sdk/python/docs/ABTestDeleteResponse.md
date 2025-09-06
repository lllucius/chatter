# ABTestDeleteResponse

Response schema for test deletion.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**success** | **bool** | Whether deletion was successful | 
**message** | **str** | Deletion result message | 

## Example

```python
from chatter_sdk.models.ab_test_delete_response import ABTestDeleteResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ABTestDeleteResponse from a JSON string
ab_test_delete_response_instance = ABTestDeleteResponse.from_json(json)
# print the JSON string representation of the object
print(ABTestDeleteResponse.to_json())

# convert the object into a dict
ab_test_delete_response_dict = ab_test_delete_response_instance.to_dict()
# create an instance of ABTestDeleteResponse from a dict
ab_test_delete_response_from_dict = ABTestDeleteResponse.from_dict(ab_test_delete_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


