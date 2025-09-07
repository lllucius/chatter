# ABTestUpdateRequest

Request schema for updating an A/B test.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**status** | [**TestStatus**](TestStatus.md) |  | [optional] 
**duration_days** | **int** |  | [optional] 
**min_sample_size** | **int** |  | [optional] 
**confidence_level** | **float** |  | [optional] 
**traffic_percentage** | **float** |  | [optional] 
**tags** | **List[str]** |  | [optional] 
**metadata** | **Dict[str, object]** |  | [optional] 

## Example

```python
from chatter_sdk.models.ab_test_update_request import ABTestUpdateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ABTestUpdateRequest from a JSON string
ab_test_update_request_instance = ABTestUpdateRequest.from_json(json)
# print the JSON string representation of the object
print(ABTestUpdateRequest.to_json())

# convert the object into a dict
ab_test_update_request_dict = ab_test_update_request_instance.to_dict()
# create an instance of ABTestUpdateRequest from a dict
ab_test_update_request_from_dict = ABTestUpdateRequest.from_dict(ab_test_update_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


