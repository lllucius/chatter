# ConversationSearchResponse

Schema for conversation search response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**conversations** | [**List[ConversationResponse]**](ConversationResponse.md) | Conversations | 
**total** | **int** | Total number of conversations | 
**limit** | **int** | Request limit | 
**offset** | **int** | Request offset | 

## Example

```python
from chatter_sdk.models.conversation_search_response import ConversationSearchResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ConversationSearchResponse from a JSON string
conversation_search_response_instance = ConversationSearchResponse.from_json(json)
# print the JSON string representation of the object
print(ConversationSearchResponse.to_json())

# convert the object into a dict
conversation_search_response_dict = conversation_search_response_instance.to_dict()
# create an instance of ConversationSearchResponse from a dict
conversation_search_response_from_dict = ConversationSearchResponse.from_dict(conversation_search_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


