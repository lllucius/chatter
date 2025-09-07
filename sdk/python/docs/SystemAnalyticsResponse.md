# SystemAnalyticsResponse

Schema for system analytics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_users** | **int** | Total number of users | 
**active_users_today** | **int** | Active users today | 
**active_users_week** | **int** | Active users this week | 
**active_users_month** | **int** | Active users this month | 
**system_uptime_seconds** | **float** | System uptime in seconds | 
**avg_cpu_usage** | **float** | Average CPU usage percentage | 
**avg_memory_usage** | **float** | Average memory usage percentage | 
**database_connections** | **int** | Current database connections | 
**total_api_requests** | **int** | Total API requests | 
**requests_per_endpoint** | **Dict[str, int]** | Requests by endpoint | 
**avg_api_response_time** | **float** | Average API response time | 
**api_error_rate** | **float** | API error rate | 
**storage_usage_bytes** | **int** | Total storage usage | 
**vector_database_size_bytes** | **int** | Vector database size | 
**cache_hit_rate** | **float** | Cache hit rate | 

## Example

```python
from chatter_sdk.models.system_analytics_response import SystemAnalyticsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SystemAnalyticsResponse from a JSON string
system_analytics_response_instance = SystemAnalyticsResponse.from_json(json)
# print the JSON string representation of the object
print(SystemAnalyticsResponse.to_json())

# convert the object into a dict
system_analytics_response_dict = system_analytics_response_instance.to_dict()
# create an instance of SystemAnalyticsResponse from a dict
system_analytics_response_from_dict = SystemAnalyticsResponse.from_dict(system_analytics_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


