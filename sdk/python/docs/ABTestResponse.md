# ABTestResponse

Response schema for A/B test data.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Test ID | 
**name** | **str** | Test name | 
**description** | **str** | Test description | 
**test_type** | [**TestType**](TestType.md) |  | 
**status** | [**TestStatus**](TestStatus.md) |  | 
**allocation_strategy** | [**VariantAllocation**](VariantAllocation.md) |  | 
**variants** | [**List[TestVariant]**](TestVariant.md) | Test variants | 
**metrics** | [**List[MetricType]**](MetricType.md) | Metrics being tracked | 
**duration_days** | **int** | Test duration in days | 
**min_sample_size** | **int** | Minimum sample size | 
**confidence_level** | **float** | Statistical confidence level | 
**target_audience** | **Dict[str, object]** |  | [optional] 
**traffic_percentage** | **float** | Percentage of traffic included | 
**start_date** | **datetime** |  | [optional] 
**end_date** | **datetime** |  | [optional] 
**participant_count** | **int** | Number of participants | [optional] [default to 0]
**created_at** | **datetime** | Creation timestamp | 
**updated_at** | **datetime** | Last update timestamp | 
**created_by** | **str** | Creator | 
**tags** | **List[str]** | Test tags | 
**metadata** | **Dict[str, object]** | Additional metadata | 

## Example

```python
from chatter_sdk.models.ab_test_response import ABTestResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ABTestResponse from a JSON string
ab_test_response_instance = ABTestResponse.from_json(json)
# print the JSON string representation of the object
print(ABTestResponse.to_json())

# convert the object into a dict
ab_test_response_dict = ab_test_response_instance.to_dict()
# create an instance of ABTestResponse from a dict
ab_test_response_from_dict = ABTestResponse.from_dict(ab_test_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


