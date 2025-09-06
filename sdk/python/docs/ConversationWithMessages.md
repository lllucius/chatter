# ConversationWithMessages

Schema for conversation with messages.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** | Conversation title | 
**description** | **str** |  | [optional] 
**id** | **str** | Conversation ID | 
**user_id** | **str** | User ID | 
**profile_id** | **str** |  | [optional] 
**status** | [**ConversationStatus**](ConversationStatus.md) |  | 
**llm_provider** | **str** |  | [optional] 
**llm_model** | **str** |  | [optional] 
**temperature** | **float** |  | [optional] 
**max_tokens** | **int** |  | [optional] 
**enable_retrieval** | **bool** | Retrieval enabled | 
**message_count** | **int** | Number of messages | 
**total_tokens** | **int** | Total tokens used | 
**total_cost** | **float** | Total cost | 
**system_prompt** | **str** |  | [optional] 
**context_window** | **int** | Context window size | 
**memory_enabled** | **bool** | Memory enabled | 
**memory_strategy** | **str** |  | [optional] 
**retrieval_limit** | **int** | Retrieval limit | 
**retrieval_score_threshold** | **float** | Retrieval score threshold | 
**tags** | **List[str]** |  | [optional] 
**extra_metadata** | **Dict[str, object]** |  | [optional] 
**workflow_config** | **Dict[str, object]** |  | [optional] 
**created_at** | **datetime** | Creation timestamp | 
**updated_at** | **datetime** | Last update timestamp | 
**last_message_at** | **datetime** |  | [optional] 
**messages** | [**List[MessageResponse]**](MessageResponse.md) | Conversation messages | [optional] 

## Example

```python
from chatter_sdk.models.conversation_with_messages import ConversationWithMessages

# TODO update the JSON string below
json = "{}"
# create an instance of ConversationWithMessages from a JSON string
conversation_with_messages_instance = ConversationWithMessages.from_json(json)
# print the JSON string representation of the object
print(ConversationWithMessages.to_json())

# convert the object into a dict
conversation_with_messages_dict = conversation_with_messages_instance.to_dict()
# create an instance of ConversationWithMessages from a dict
conversation_with_messages_from_dict = ConversationWithMessages.from_dict(conversation_with_messages_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


