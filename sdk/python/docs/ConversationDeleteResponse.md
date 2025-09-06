# ConversationDeleteResponse

Schema for conversation delete response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | Success message | 

## Example

```python
from chatter_sdk.models.conversation_delete_response import ConversationDeleteResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ConversationDeleteResponse from a JSON string
conversation_delete_response_instance = ConversationDeleteResponse.from_json(json)
# print the JSON string representation of the object
print(ConversationDeleteResponse.to_json())

# convert the object into a dict
conversation_delete_response_dict = conversation_delete_response_instance.to_dict()
# create an instance of ConversationDeleteResponse from a dict
conversation_delete_response_from_dict = ConversationDeleteResponse.from_dict(conversation_delete_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


