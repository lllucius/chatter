# MetricsSummaryResponse

Schema for metrics summary response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_metrics** | **int** | Total number of metrics | 
**active_metrics** | **int** | Number of active metrics | 
**data_points_last_hour** | **int** | Data points collected in last hour | 
**storage_size_mb** | **float** | Storage size in MB | 
**oldest_data_point** | **datetime** |  | [optional] 
**latest_data_point** | **datetime** |  | [optional] 

## Example

```python
from chatter_sdk.models.metrics_summary_response import MetricsSummaryResponse

# TODO update the JSON string below
json = "{}"
# create an instance of MetricsSummaryResponse from a JSON string
metrics_summary_response_instance = MetricsSummaryResponse.from_json(json)
# print the JSON string representation of the object
print(MetricsSummaryResponse.to_json())

# convert the object into a dict
metrics_summary_response_dict = metrics_summary_response_instance.to_dict()
# create an instance of MetricsSummaryResponse from a dict
metrics_summary_response_from_dict = MetricsSummaryResponse.from_dict(metrics_summary_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


