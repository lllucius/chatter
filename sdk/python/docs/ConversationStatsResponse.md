# ConversationStatsResponse

Schema for conversation statistics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_conversations** | **int** | Total number of conversations | 
**conversations_by_status** | **Dict[str, int]** | Conversations grouped by status | 
**total_messages** | **int** | Total number of messages | 
**messages_by_role** | **Dict[str, int]** | Messages grouped by role | 
**avg_messages_per_conversation** | **float** | Average messages per conversation | 
**total_tokens_used** | **int** | Total tokens used | 
**total_cost** | **float** | Total cost incurred | 
**avg_response_time_ms** | **float** | Average response time in milliseconds | 
**conversations_by_date** | **Dict[str, int]** | Conversations by date | 
**most_active_hours** | **Dict[str, int]** | Most active hours | 
**popular_models** | **Dict[str, int]** | Popular LLM models | 
**popular_providers** | **Dict[str, int]** | Popular LLM providers | 
**total_ratings** | **int** | Total number of message ratings | [optional] [default to 0]
**avg_message_rating** | **float** | Average message rating | [optional] [default to 0.0]
**messages_with_ratings** | **int** | Number of messages with ratings | [optional] [default to 0]
**rating_distribution** | **Dict[str, int]** | Distribution of ratings (1-5 stars) | [optional] 

## Example

```python
from chatter_sdk.models.conversation_stats_response import ConversationStatsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ConversationStatsResponse from a JSON string
conversation_stats_response_instance = ConversationStatsResponse.from_json(json)
# print the JSON string representation of the object
print(ConversationStatsResponse.to_json())

# convert the object into a dict
conversation_stats_response_dict = conversation_stats_response_instance.to_dict()
# create an instance of ConversationStatsResponse from a dict
conversation_stats_response_from_dict = ConversationStatsResponse.from_dict(conversation_stats_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


