# PerformanceMetricsResponse

Schema for performance metrics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**avg_response_time_ms** | **float** | Average response time | 
**median_response_time_ms** | **float** | Median response time | 
**p95_response_time_ms** | **float** | 95th percentile response time | 
**p99_response_time_ms** | **float** | 99th percentile response time | 
**requests_per_minute** | **float** | Average requests per minute | 
**tokens_per_minute** | **float** | Average tokens per minute | 
**total_errors** | **int** | Total number of errors | 
**error_rate** | **float** | Error rate percentage | 
**errors_by_type** | **Dict[str, int]** | Errors grouped by type | 
**performance_by_model** | **Dict[str, Dict[str, float]]** | Performance metrics by model | 
**performance_by_provider** | **Dict[str, Dict[str, float]]** | Performance metrics by provider | 
**database_response_time_ms** | **float** | Average database response time | 
**vector_search_time_ms** | **float** | Average vector search time | 
**embedding_generation_time_ms** | **float** | Average embedding generation time | 

## Example

```python
from chatter_sdk.models.performance_metrics_response import PerformanceMetricsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PerformanceMetricsResponse from a JSON string
performance_metrics_response_instance = PerformanceMetricsResponse.from_json(json)
# print the JSON string representation of the object
print(PerformanceMetricsResponse.to_json())

# convert the object into a dict
performance_metrics_response_dict = performance_metrics_response_instance.to_dict()
# create an instance of PerformanceMetricsResponse from a dict
performance_metrics_response_from_dict = PerformanceMetricsResponse.from_dict(performance_metrics_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


