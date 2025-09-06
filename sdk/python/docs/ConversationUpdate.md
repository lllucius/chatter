# ConversationUpdate

Schema for updating a conversation.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**status** | [**ConversationStatus**](ConversationStatus.md) |  | [optional] 
**temperature** | **float** |  | [optional] 
**max_tokens** | **int** |  | [optional] 
**workflow_config** | **Dict[str, object]** |  | [optional] 
**extra_metadata** | **Dict[str, object]** |  | [optional] 

## Example

```python
from chatter_sdk.models.conversation_update import ConversationUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of ConversationUpdate from a JSON string
conversation_update_instance = ConversationUpdate.from_json(json)
# print the JSON string representation of the object
print(ConversationUpdate.to_json())

# convert the object into a dict
conversation_update_dict = conversation_update_instance.to_dict()
# create an instance of ConversationUpdate from a dict
conversation_update_from_dict = ConversationUpdate.from_dict(conversation_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


