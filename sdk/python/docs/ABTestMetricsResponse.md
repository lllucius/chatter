# ABTestMetricsResponse

Response schema for A/B test metrics.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test_id** | **str** | Test ID | 
**metrics** | [**List[TestMetric]**](TestMetric.md) | Current metrics | 
**participant_count** | **int** | Current participant count | 
**last_updated** | **datetime** | Last metrics update | 

## Example

```python
from chatter_sdk.models.ab_test_metrics_response import ABTestMetricsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ABTestMetricsResponse from a JSON string
ab_test_metrics_response_instance = ABTestMetricsResponse.from_json(json)
# print the JSON string representation of the object
print(ABTestMetricsResponse.to_json())

# convert the object into a dict
ab_test_metrics_response_dict = ab_test_metrics_response_instance.to_dict()
# create an instance of ABTestMetricsResponse from a dict
ab_test_metrics_response_from_dict = ABTestMetricsResponse.from_dict(ab_test_metrics_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


