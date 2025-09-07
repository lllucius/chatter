# MessageDeleteResponse

Response schema for message deletion.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Deletion result message | 

## Example

```python
from chatter_sdk.models.message_delete_response import MessageDeleteResponse

# TODO update the JSON string below
json = "{}"
# create an instance of MessageDeleteResponse from a JSON string
message_delete_response_instance = MessageDeleteResponse.from_json(json)
# print the JSON string representation of the object
print(MessageDeleteResponse.to_json())

# convert the object into a dict
message_delete_response_dict = message_delete_response_instance.to_dict()
# create an instance of MessageDeleteResponse from a dict
message_delete_response_from_dict = MessageDeleteResponse.from_dict(message_delete_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


