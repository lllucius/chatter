# PerformanceStatsResponse

Schema for performance statistics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_executions** | **int** | Total number of executions | 
**avg_execution_time_ms** | **int** | Average execution time in milliseconds | 
**min_execution_time_ms** | **int** | Minimum execution time in milliseconds | 
**max_execution_time_ms** | **int** | Maximum execution time in milliseconds | 
**workflow_types** | **Dict[str, int]** | Execution count by workflow type | 
**error_counts** | **Dict[str, int]** | Error count by type | 
**cache_stats** | **Dict[str, object]** | Cache statistics | 
**tool_stats** | **Dict[str, object]** | Tool usage statistics | 
**timestamp** | **float** | Statistics timestamp | 

## Example

```python
from chatter_sdk.models.performance_stats_response import PerformanceStatsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PerformanceStatsResponse from a JSON string
performance_stats_response_instance = PerformanceStatsResponse.from_json(json)
# print the JSON string representation of the object
print(PerformanceStatsResponse.to_json())

# convert the object into a dict
performance_stats_response_dict = performance_stats_response_instance.to_dict()
# create an instance of PerformanceStatsResponse from a dict
performance_stats_response_from_dict = PerformanceStatsResponse.from_dict(performance_stats_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


