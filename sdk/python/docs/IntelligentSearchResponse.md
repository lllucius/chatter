# IntelligentSearchResponse

Schema for intelligent search response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**query** | **str** | Search query | 
**results** | **List[Dict[str, object]]** | Search results | 
**suggestions** | **List[str]** | Search suggestions | 
**analytics** | **Dict[str, object]** | Search analytics | 
**response_time_ms** | **float** | Response time in milliseconds | 

## Example

```python
from chatter_sdk.models.intelligent_search_response import IntelligentSearchResponse

# TODO update the JSON string below
json = "{}"
# create an instance of IntelligentSearchResponse from a JSON string
intelligent_search_response_instance = IntelligentSearchResponse.from_json(json)
# print the JSON string representation of the object
print(IntelligentSearchResponse.to_json())

# convert the object into a dict
intelligent_search_response_dict = intelligent_search_response_instance.to_dict()
# create an instance of IntelligentSearchResponse from a dict
intelligent_search_response_from_dict = IntelligentSearchResponse.from_dict(intelligent_search_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


