# ChatterSchemasChatWorkflowTemplatesResponse

Schema for workflow templates response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**templates** | [**Dict[str, WorkflowTemplateInfo]**](WorkflowTemplateInfo.md) | Available templates | 
**total_count** | **int** | Total number of templates | 

## Example

```python
from chatter_sdk.models.chatter_schemas_chat_workflow_templates_response import ChatterSchemasChatWorkflowTemplatesResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ChatterSchemasChatWorkflowTemplatesResponse from a JSON string
chatter_schemas_chat_workflow_templates_response_instance = ChatterSchemasChatWorkflowTemplatesResponse.from_json(json)
# print the JSON string representation of the object
print(ChatterSchemasChatWorkflowTemplatesResponse.to_json())

# convert the object into a dict
chatter_schemas_chat_workflow_templates_response_dict = chatter_schemas_chat_workflow_templates_response_instance.to_dict()
# create an instance of ChatterSchemasChatWorkflowTemplatesResponse from a dict
chatter_schemas_chat_workflow_templates_response_from_dict = ChatterSchemasChatWorkflowTemplatesResponse.from_dict(chatter_schemas_chat_workflow_templates_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


