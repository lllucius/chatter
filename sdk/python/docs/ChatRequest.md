# ChatRequest

Schema for chat request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | User message | 
**conversation_id** | **str** |  | [optional] 
**profile_id** | **str** |  | [optional] 
**stream** | **bool** | Enable streaming response | [optional] [default to False]
**workflow** | **str** | Workflow type: plain, rag, tools, or full (rag + tools) | [optional] [default to 'plain']
**provider** | **str** |  | [optional] 
**temperature** | **float** |  | [optional] 
**max_tokens** | **int** |  | [optional] 
**context_limit** | **int** |  | [optional] 
**enable_retrieval** | **bool** |  | [optional] 
**document_ids** | **List[str]** |  | [optional] 
**system_prompt_override** | **str** |  | [optional] 
**workflow_config** | **Dict[str, object]** |  | [optional] 
**workflow_type** | **str** |  | [optional] 

## Example

```python
from chatter_sdk.models.chat_request import ChatRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ChatRequest from a JSON string
chat_request_instance = ChatRequest.from_json(json)
# print the JSON string representation of the object
print(ChatRequest.to_json())

# convert the object into a dict
chat_request_dict = chat_request_instance.to_dict()
# create an instance of ChatRequest from a dict
chat_request_from_dict = ChatRequest.from_dict(chat_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


