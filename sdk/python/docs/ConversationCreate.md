# ConversationCreate

Schema for creating a conversation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** | Conversation title | 
**description** | **str** |  | [optional] 
**profile_id** | **str** |  | [optional] 
**system_prompt** | **str** |  | [optional] 
**enable_retrieval** | **bool** | Enable document retrieval | [optional] [default to False]
**temperature** | **float** |  | [optional] 
**max_tokens** | **int** |  | [optional] 
**workflow_config** | **Dict[str, object]** |  | [optional] 
**extra_metadata** | **Dict[str, object]** |  | [optional] 

## Example

```python
from chatter_sdk.models.conversation_create import ConversationCreate

# TODO update the JSON string below
json = "{}"
# create an instance of ConversationCreate from a JSON string
conversation_create_instance = ConversationCreate.from_json(json)
# print the JSON string representation of the object
print(ConversationCreate.to_json())

# convert the object into a dict
conversation_create_dict = conversation_create_instance.to_dict()
# create an instance of ConversationCreate from a dict
conversation_create_from_dict = ConversationCreate.from_dict(conversation_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


