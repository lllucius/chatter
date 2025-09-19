# ChatWorkflowTemplatesResponse

Response for chat workflow templates.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**templates** | [**Dict[str, ChatWorkflowTemplate]**](ChatWorkflowTemplate.md) | Available templates | 
**total_count** | **int** | Total template count | 

## Example

```python
from chatter_sdk.models.chat_workflow_templates_response import ChatWorkflowTemplatesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ChatWorkflowTemplatesResponse from a JSON string
chat_workflow_templates_response_instance = ChatWorkflowTemplatesResponse.from_json(json)
# print the JSON string representation of the object
print(ChatWorkflowTemplatesResponse.to_json())

# convert the object into a dict
chat_workflow_templates_response_dict = chat_workflow_templates_response_instance.to_dict()
# create an instance of ChatWorkflowTemplatesResponse from a dict
chat_workflow_templates_response_from_dict = ChatWorkflowTemplatesResponse.from_dict(chat_workflow_templates_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


