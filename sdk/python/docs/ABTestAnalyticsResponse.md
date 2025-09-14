# ABTestAnalyticsResponse

Comprehensive A/B test analytics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test_id** | **str** | Test ID | 
**test_name** | **str** | Test name | 
**status** | [**TestStatus**](TestStatus.md) |  | 
**total_participants** | **int** | Total participants | 
**variants** | [**List[VariantPerformance]**](VariantPerformance.md) | Variant performance data | 
**statistical_analysis** | [**StatisticalAnalysis**](StatisticalAnalysis.md) |  | 
**winner** | **str** |  | [optional] 
**improvement** | **float** |  | [optional] 
**recommendation** | **str** | Recommendation | 
**duration_days** | **int** | Days test has been running | 
**remaining_days** | **int** |  | [optional] 
**progress_percentage** | **float** | Test progress percentage | 
**generated_at** | **datetime** | Analytics generation timestamp | 
**last_updated** | **datetime** | Last data update | 

## Example

```python
from chatter_sdk.models.ab_test_analytics_response import ABTestAnalyticsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ABTestAnalyticsResponse from a JSON string
ab_test_analytics_response_instance = ABTestAnalyticsResponse.from_json(json)
# print the JSON string representation of the object
print(ABTestAnalyticsResponse.to_json())

# convert the object into a dict
ab_test_analytics_response_dict = ab_test_analytics_response_instance.to_dict()
# create an instance of ABTestAnalyticsResponse from a dict
ab_test_analytics_response_from_dict = ABTestAnalyticsResponse.from_dict(ab_test_analytics_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


