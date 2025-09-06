# SSEStatsResponse

Response schema for SSE service statistics.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_connections** | **int** | Total active connections | 
**your_connections** | **int** | Your active connections | 

## Example

```python
from chatter_sdk.models.sse_stats_response import SSEStatsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SSEStatsResponse from a JSON string
sse_stats_response_instance = SSEStatsResponse.from_json(json)
# print the JSON string representation of the object
print(SSEStatsResponse.to_json())

# convert the object into a dict
sse_stats_response_dict = sse_stats_response_instance.to_dict()
# create an instance of SSEStatsResponse from a dict
sse_stats_response_from_dict = SSEStatsResponse.from_dict(sse_stats_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


