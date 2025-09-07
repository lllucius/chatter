# ABTestCreateRequest

Request schema for creating an A/B test.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Test name | 
**description** | **str** | Test description | 
**test_type** | [**TestType**](TestType.md) |  | 
**allocation_strategy** | [**VariantAllocation**](VariantAllocation.md) |  | 
**variants** | [**List[TestVariant]**](TestVariant.md) | Test variants | 
**metrics** | [**List[MetricType]**](MetricType.md) | Metrics to track | 
**duration_days** | **int** | Test duration in days | [optional] [default to 7]
**min_sample_size** | **int** | Minimum sample size | [optional] [default to 100]
**confidence_level** | **float** | Statistical confidence level | [optional] [default to 0.95]
**target_audience** | **Dict[str, object]** |  | [optional] 
**traffic_percentage** | **float** | Percentage of traffic to include | [optional] [default to 100.0]
**tags** | **List[str]** | Test tags | [optional] 
**metadata** | **Dict[str, object]** | Additional metadata | [optional] 

## Example

```python
from chatter_sdk.models.ab_test_create_request import ABTestCreateRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ABTestCreateRequest from a JSON string
ab_test_create_request_instance = ABTestCreateRequest.from_json(json)
# print the JSON string representation of the object
print(ABTestCreateRequest.to_json())

# convert the object into a dict
ab_test_create_request_dict = ab_test_create_request_instance.to_dict()
# create an instance of ABTestCreateRequest from a dict
ab_test_create_request_from_dict = ABTestCreateRequest.from_dict(ab_test_create_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


