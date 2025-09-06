# PromptTestResponse

Schema for prompt test response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rendered_content** | **str** |  | [optional] 
**validation_result** | **Dict[str, object]** | Validation results | 
**estimated_tokens** | **int** |  | [optional] 
**test_duration_ms** | **int** | Test execution time | 
**template_variables_used** | **List[str]** | Template variables actually used | 
**security_warnings** | **List[str]** | Security warnings if any | [optional] 
**performance_metrics** | **Dict[str, object]** |  | [optional] 

## Example

```python
from chatter_sdk.models.prompt_test_response import PromptTestResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PromptTestResponse from a JSON string
prompt_test_response_instance = PromptTestResponse.from_json(json)
# print the JSON string representation of the object
print(PromptTestResponse.to_json())

# convert the object into a dict
prompt_test_response_dict = prompt_test_response_instance.to_dict()
# create an instance of PromptTestResponse from a dict
prompt_test_response_from_dict = PromptTestResponse.from_dict(prompt_test_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


