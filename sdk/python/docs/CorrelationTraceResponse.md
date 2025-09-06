# CorrelationTraceResponse

Schema for correlation trace response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**correlation_id** | **str** | Correlation ID | 
**trace_length** | **int** | Number of requests in trace | 
**requests** | **List[Dict[str, object]]** | List of requests in trace | 

## Example

```python
from chatter_sdk.models.correlation_trace_response import CorrelationTraceResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CorrelationTraceResponse from a JSON string
correlation_trace_response_instance = CorrelationTraceResponse.from_json(json)
# print the JSON string representation of the object
print(CorrelationTraceResponse.to_json())

# convert the object into a dict
correlation_trace_response_dict = correlation_trace_response_instance.to_dict()
# create an instance of CorrelationTraceResponse from a dict
correlation_trace_response_from_dict = CorrelationTraceResponse.from_dict(correlation_trace_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


