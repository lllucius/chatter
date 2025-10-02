# ChatRequest

Schema for chat request.  This unified schema supports both simple chat and workflow execution, eliminating the need for separate ChatWorkflowRequest type.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | User message | 
**conversation_id** | **str** |  | [optional] 
**profile_id** | **str** |  | [optional] 
**workflow_config** | **Dict[str, object]** |  | [optional] 
**workflow_definition_id** | **str** |  | [optional] 
**workflow_template_name** | **str** |  | [optional] 
**enable_retrieval** | **bool** | Enable retrieval capabilities | [optional] [default to False]
**enable_tools** | **bool** | Enable tool calling capabilities | [optional] [default to False]
**enable_memory** | **bool** | Enable memory capabilities | [optional] [default to True]
**enable_web_search** | **bool** | Enable web search capabilities | [optional] [default to False]
**provider** | **str** |  | [optional] 
**model** | **str** |  | [optional] 
**temperature** | **float** |  | [optional] 
**max_tokens** | **int** |  | [optional] 
**context_limit** | **int** |  | [optional] 
**document_ids** | **List[str]** |  | [optional] 
**prompt_id** | **str** |  | [optional] 
**system_prompt_override** | **str** |  | [optional] 
**enable_tracing** | **bool** | Enable backend workflow tracing | [optional] [default to False]

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


