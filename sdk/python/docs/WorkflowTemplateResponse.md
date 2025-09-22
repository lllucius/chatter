# WorkflowTemplateResponse

Schema for workflow template response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Template name | 
**description** | **str** | Template description | 
**category** | **str** | Template category | [optional] [default to 'custom']
**default_params** | **Dict[str, object]** | Default parameters | [optional] 
**required_tools** | **List[str]** |  | [optional] 
**required_retrievers** | **List[str]** |  | [optional] 
**tags** | **List[str]** |  | [optional] 
**is_public** | **bool** | Whether template is public | [optional] [default to False]
**id** | **str** | Unique node identifier | 
**owner_id** | **str** | Owner user ID | 
**base_template_id** | **str** |  | [optional] 
**is_builtin** | **bool** | Whether template is built-in | [optional] [default to False]
**version** | **int** | Template version | [optional] [default to 1]
**is_latest** | **bool** | Whether this is the latest version | [optional] [default to True]
**rating** | **float** |  | [optional] 
**rating_count** | **int** | Number of ratings | [optional] [default to 0]
**usage_count** | **int** | Usage count | [optional] [default to 0]
**success_rate** | **float** |  | [optional] 
**config_hash** | **str** | Configuration hash | 
**estimated_complexity** | **int** |  | [optional] 

## Example

```python
from chatter_sdk.models.workflow_template_response import WorkflowTemplateResponse

# TODO update the JSON string below
json = "{}"
# create an instance of WorkflowTemplateResponse from a JSON string
workflow_template_response_instance = WorkflowTemplateResponse.from_json(json)
# print the JSON string representation of the object
print(WorkflowTemplateResponse.to_json())

# convert the object into a dict
workflow_template_response_dict = workflow_template_response_instance.to_dict()
# create an instance of WorkflowTemplateResponse from a dict
workflow_template_response_from_dict = WorkflowTemplateResponse.from_dict(workflow_template_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


