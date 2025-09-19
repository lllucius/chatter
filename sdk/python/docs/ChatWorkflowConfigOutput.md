# ChatWorkflowConfigOutput

Configuration for building chat workflows dynamically.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**enable_retrieval** | **bool** | Enable document retrieval | [optional] [default to False]
**enable_tools** | **bool** | Enable function calling | [optional] [default to False]
**enable_memory** | **bool** | Enable conversation memory | [optional] [default to True]
**enable_web_search** | **bool** | Enable web search | [optional] [default to False]
**llm_config** | [**ModelConfig**](ModelConfig.md) |  | [optional] 
**retrieval_config** | [**RetrievalConfig**](RetrievalConfig.md) |  | [optional] 
**tool_config** | [**ToolConfig**](ToolConfig.md) |  | [optional] 
**custom_nodes** | [**List[WorkflowNode]**](WorkflowNode.md) |  | [optional] 
**custom_edges** | [**List[WorkflowEdge]**](WorkflowEdge.md) |  | [optional] 

## Example

```python
from chatter_sdk.models.chat_workflow_config_output import ChatWorkflowConfigOutput

# TODO update the JSON string below
json = "{}"
# create an instance of ChatWorkflowConfigOutput from a JSON string
chat_workflow_config_output_instance = ChatWorkflowConfigOutput.from_json(json)
# print the JSON string representation of the object
print(ChatWorkflowConfigOutput.to_json())

# convert the object into a dict
chat_workflow_config_output_dict = chat_workflow_config_output_instance.to_dict()
# create an instance of ChatWorkflowConfigOutput from a dict
chat_workflow_config_output_from_dict = ChatWorkflowConfigOutput.from_dict(chat_workflow_config_output_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


