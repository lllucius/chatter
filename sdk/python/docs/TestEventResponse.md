# TestEventResponse

Response schema for test event.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Response message | 
**event_id** | **str** | Generated event ID | 

## Example

```python
from chatter_sdk.models.test_event_response import TestEventResponse

# TODO update the JSON string below
json = "{}"
# create an instance of TestEventResponse from a JSON string
test_event_response_instance = TestEventResponse.from_json(json)
# print the JSON string representation of the object
print(TestEventResponse.to_json())

# convert the object into a dict
test_event_response_dict = test_event_response_instance.to_dict()
# create an instance of TestEventResponse from a dict
test_event_response_from_dict = TestEventResponse.from_dict(test_event_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


