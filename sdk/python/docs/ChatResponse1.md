# ChatResponse1

Schema for chat response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**conversation_id** | **str** | Conversation ID | 
**message** | [**MessageResponse**](MessageResponse.md) |  | 
**conversation** | [**ConversationResponse**](ConversationResponse.md) |  | 

## Example

```python
from chatter_sdk.models.chat_response1 import ChatResponse1

# TODO update the JSON string below
json = "{}"
# create an instance of ChatResponse1 from a JSON string
chat_response1_instance = ChatResponse1.from_json(json)
# print the JSON string representation of the object
print(ChatResponse1.to_json())

# convert the object into a dict
chat_response1_dict = chat_response1_instance.to_dict()
# create an instance of ChatResponse1 from a dict
chat_response1_from_dict = ChatResponse1.from_dict(chat_response1_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


