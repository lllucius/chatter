# OptimizationSuggestion

Schema for optimization suggestions.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** | Suggestion type | 
**description** | **str** | Suggestion description | 
**impact** | **str** | Expected impact (low/medium/high) | 
**node_ids** | **List[str]** |  | [optional] 

## Example

```python
from chatter_sdk.models.optimization_suggestion import OptimizationSuggestion

# TODO update the JSON string below
json = "{}"
# create an instance of OptimizationSuggestion from a JSON string
optimization_suggestion_instance = OptimizationSuggestion.from_json(json)
# print the JSON string representation of the object
print(OptimizationSuggestion.to_json())

# convert the object into a dict
optimization_suggestion_dict = optimization_suggestion_instance.to_dict()
# create an instance of OptimizationSuggestion from a dict
optimization_suggestion_from_dict = OptimizationSuggestion.from_dict(optimization_suggestion_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


