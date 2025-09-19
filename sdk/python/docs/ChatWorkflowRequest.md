# ChatWorkflowRequest

Request for executing chat via workflow system.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**message** | **str** | User message | 
**conversation_id** | **str** |  | [optional] 
**workflow_config** | [**ChatWorkflowConfigInput**](ChatWorkflowConfigInput.md) |  | [optional] 
**workflow_definition_id** | **str** |  | [optional] 
**workflow_template_name** | **str** |  | [optional] 
**profile_id** | **str** |  | [optional] 
**provider** | **str** |  | [optional] 
**temperature** | **float** |  | [optional] 
**max_tokens** | **int** |  | [optional] 
**context_limit** | **int** |  | [optional] 
**document_ids** | **List[str]** |  | [optional] 
**system_prompt_override** | **str** |  | [optional] 

## Example

```python
from chatter_sdk.models.chat_workflow_request import ChatWorkflowRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ChatWorkflowRequest from a JSON string
chat_workflow_request_instance = ChatWorkflowRequest.from_json(json)
# print the JSON string representation of the object
print(ChatWorkflowRequest.to_json())

# convert the object into a dict
chat_workflow_request_dict = chat_workflow_request_instance.to_dict()
# create an instance of ChatWorkflowRequest from a dict
chat_workflow_request_from_dict = ChatWorkflowRequest.from_dict(chat_workflow_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


