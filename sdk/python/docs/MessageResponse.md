# MessageResponse

Schema for message response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**role** | [**MessageRole**](MessageRole.md) |  | 
**content** | **str** | Message content | 
**id** | **str** | Message ID | 
**conversation_id** | **str** | Conversation ID | 
**sequence_number** | **int** | Message sequence number | 
**prompt_tokens** | **int** |  | [optional] 
**completion_tokens** | **int** |  | [optional] 
**total_tokens** | **int** |  | [optional] 
**model_used** | **str** |  | [optional] 
**provider_used** | **str** |  | [optional] 
**response_time_ms** | **int** |  | [optional] 
**cost** | **float** |  | [optional] 
**finish_reason** | **str** |  | [optional] 
**rating** | **float** |  | [optional] 
**rating_count** | **int** | Number of ratings for the message | [optional] [default to 0]
**created_at** | **datetime** | Creation timestamp | 

## Example

```python
from chatter_sdk.models.message_response import MessageResponse

# TODO update the JSON string below
json = "{}"
# create an instance of MessageResponse from a JSON string
message_response_instance = MessageResponse.from_json(json)
# print the JSON string representation of the object
print(MessageResponse.to_json())

# convert the object into a dict
message_response_dict = message_response_instance.to_dict()
# create an instance of MessageResponse from a dict
message_response_from_dict = MessageResponse.from_dict(message_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


