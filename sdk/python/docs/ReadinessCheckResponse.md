# ReadinessCheckResponse

Schema for readiness check response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**ReadinessStatus**](ReadinessStatus.md) |  | 
**service** | **str** | Service name | 
**version** | **str** | Service version | 
**environment** | **str** | Environment | 
**checks** | **Dict[str, object]** | Health check results | 

## Example

```python
from chatter_sdk.models.readiness_check_response import ReadinessCheckResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ReadinessCheckResponse from a JSON string
readiness_check_response_instance = ReadinessCheckResponse.from_json(json)
# print the JSON string representation of the object
print(ReadinessCheckResponse.to_json())

# convert the object into a dict
readiness_check_response_dict = readiness_check_response_instance.to_dict()
# create an instance of ReadinessCheckResponse from a dict
readiness_check_response_from_dict = ReadinessCheckResponse.from_dict(readiness_check_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


