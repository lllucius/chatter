# PromptTestRequest

Schema for prompt test request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**variables** | **Dict[str, object]** | Variables to test with | 
**validate_only** | **bool** | Only validate, don&#39;t render | [optional] [default to False]
**include_performance_metrics** | **bool** | Include detailed performance metrics | [optional] [default to False]
**timeout_ms** | **int** | Test timeout in milliseconds | [optional] [default to 30000]

## Example

```python
from chatter_sdk.models.prompt_test_request import PromptTestRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PromptTestRequest from a JSON string
prompt_test_request_instance = PromptTestRequest.from_json(json)
# print the JSON string representation of the object
print(PromptTestRequest.to_json())

# convert the object into a dict
prompt_test_request_dict = prompt_test_request_instance.to_dict()
# create an instance of PromptTestRequest from a dict
prompt_test_request_from_dict = PromptTestRequest.from_dict(prompt_test_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


