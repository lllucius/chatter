# ChatWorkflowTemplate

Chat-optimized workflow template.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Template name | 
**description** | **str** | Template description | 
**config** | [**ChatWorkflowConfigOutput**](ChatWorkflowConfigOutput.md) |  | 
**estimated_tokens** | **int** |  | [optional] 
**estimated_cost** | **float** |  | [optional] 
**complexity_score** | **int** | Complexity score | [optional] [default to 1]
**use_cases** | **List[str]** | Use cases | [optional] 

## Example

```python
from chatter_sdk.models.chat_workflow_template import ChatWorkflowTemplate

# TODO update the JSON string below
json = "{}"
# create an instance of ChatWorkflowTemplate from a JSON string
chat_workflow_template_instance = ChatWorkflowTemplate.from_json(json)
# print the JSON string representation of the object
print(ChatWorkflowTemplate.to_json())

# convert the object into a dict
chat_workflow_template_dict = chat_workflow_template_instance.to_dict()
# create an instance of ChatWorkflowTemplate from a dict
chat_workflow_template_from_dict = ChatWorkflowTemplate.from_dict(chat_workflow_template_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


