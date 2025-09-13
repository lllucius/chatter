# ConversationListResponse

Schema for conversation list response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**conversations** | [**List[ConversationResponse]**](ConversationResponse.md) | List of conversations | 
**total_count** | **int** | Total number of conversations | 
**limit** | **int** | Applied limit | 
**offset** | **int** | Applied offset | 

## Example

```python
from chatter_sdk.models.conversation_list_response import ConversationListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ConversationListResponse from a JSON string
conversation_list_response_instance = ConversationListResponse.from_json(json)
# print the JSON string representation of the object
print(ConversationListResponse.to_json())

# convert the object into a dict
conversation_list_response_dict = conversation_list_response_instance.to_dict()
# create an instance of ConversationListResponse from a dict
conversation_list_response_from_dict = ConversationListResponse.from_dict(conversation_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


