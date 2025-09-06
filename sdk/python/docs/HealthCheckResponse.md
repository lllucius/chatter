# HealthCheckResponse

Schema for health check response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**HealthStatus**](HealthStatus.md) |  | 
**service** | **str** | Service name | 
**version** | **str** | Service version | 
**environment** | **str** | Environment | 

## Example

```python
from chatter_sdk.models.health_check_response import HealthCheckResponse

# TODO update the JSON string below
json = "{}"
# create an instance of HealthCheckResponse from a JSON string
health_check_response_instance = HealthCheckResponse.from_json(json)
# print the JSON string representation of the object
print(HealthCheckResponse.to_json())

# convert the object into a dict
health_check_response_dict = health_check_response_instance.to_dict()
# create an instance of HealthCheckResponse from a dict
health_check_response_from_dict = HealthCheckResponse.from_dict(health_check_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


