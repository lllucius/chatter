# AnalyticsHealthResponse

Schema for analytics health check response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Health status | 
**database_connected** | **bool** | Database connection status | 
**cache_connected** | **bool** | Cache connection status | 
**last_check** | **datetime** | Last health check timestamp | 
**services** | **Dict[str, str]** | Service status details | 

## Example

```python
from chatter_sdk.models.analytics_health_response import AnalyticsHealthResponse

# TODO update the JSON string below
json = "{}"
# create an instance of AnalyticsHealthResponse from a JSON string
analytics_health_response_instance = AnalyticsHealthResponse.from_json(json)
# print the JSON string representation of the object
print(AnalyticsHealthResponse.to_json())

# convert the object into a dict
analytics_health_response_dict = analytics_health_response_instance.to_dict()
# create an instance of AnalyticsHealthResponse from a dict
analytics_health_response_from_dict = AnalyticsHealthResponse.from_dict(analytics_health_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


