# MetricsResponse

Schema for application metrics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**timestamp** | **str** | Metrics collection timestamp (ISO 8601) | 
**service** | **str** | Service name | 
**version** | **str** | Service version | 
**environment** | **str** | Environment | 
**health** | **Dict[str, object]** | Health metrics | 
**performance** | **Dict[str, object]** | Performance statistics | 
**endpoints** | **Dict[str, object]** | Endpoint statistics | 

## Example

```python
from chatter_sdk.models.metrics_response import MetricsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of MetricsResponse from a JSON string
metrics_response_instance = MetricsResponse.from_json(json)
# print the JSON string representation of the object
print(MetricsResponse.to_json())

# convert the object into a dict
metrics_response_dict = metrics_response_instance.to_dict()
# create an instance of MetricsResponse from a dict
metrics_response_from_dict = MetricsResponse.from_dict(metrics_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


