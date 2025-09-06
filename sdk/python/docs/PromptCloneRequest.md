# PromptCloneRequest

Schema for prompt clone request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | New prompt name | 
**description** | **str** |  | [optional] 
**modifications** | **Dict[str, object]** |  | [optional] 

## Example

```python
from chatter_sdk.models.prompt_clone_request import PromptCloneRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PromptCloneRequest from a JSON string
prompt_clone_request_instance = PromptCloneRequest.from_json(json)
# print the JSON string representation of the object
print(PromptCloneRequest.to_json())

# convert the object into a dict
prompt_clone_request_dict = prompt_clone_request_instance.to_dict()
# create an instance of PromptCloneRequest from a dict
prompt_clone_request_from_dict = PromptCloneRequest.from_dict(prompt_clone_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


