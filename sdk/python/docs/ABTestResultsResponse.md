# ABTestResultsResponse

Response schema for A/B test results.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**test_id** | **str** | Test ID | 
**test_name** | **str** | Test name | 
**status** | [**TestStatus**](TestStatus.md) |  | 
**metrics** | [**List[TestMetric]**](TestMetric.md) | Metric results by variant | 
**statistical_significance** | **Dict[str, bool]** | Statistical significance by metric | 
**confidence_intervals** | **Dict[str, Dict[str, List[float]]]** | Confidence intervals | 
**winning_variant** | **str** |  | [optional] 
**recommendation** | **str** | Action recommendation | 
**generated_at** | **datetime** | Results generation timestamp | 
**sample_size** | **int** | Total sample size | 
**duration_days** | **int** | Test duration so far | 

## Example

```python
from chatter_sdk.models.ab_test_results_response import ABTestResultsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ABTestResultsResponse from a JSON string
ab_test_results_response_instance = ABTestResultsResponse.from_json(json)
# print the JSON string representation of the object
print(ABTestResultsResponse.to_json())

# convert the object into a dict
ab_test_results_response_dict = ab_test_results_response_instance.to_dict()
# create an instance of ABTestResultsResponse from a dict
ab_test_results_response_from_dict = ABTestResultsResponse.from_dict(ab_test_results_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


