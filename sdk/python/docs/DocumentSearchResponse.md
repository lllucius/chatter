# DocumentSearchResponse

Schema for document search response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**results** | [**List[DocumentSearchResult]**](DocumentSearchResult.md) | Search results | 
**total_results** | **int** | Total number of matching results | 
**query** | **str** | Original search query | 
**score_threshold** | **float** | Applied score threshold | 

## Example

```python
from chatter_sdk.models.document_search_response import DocumentSearchResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentSearchResponse from a JSON string
document_search_response_instance = DocumentSearchResponse.from_json(json)
# print the JSON string representation of the object
print(DocumentSearchResponse.to_json())

# convert the object into a dict
document_search_response_dict = document_search_response_instance.to_dict()
# create an instance of DocumentSearchResponse from a dict
document_search_response_from_dict = DocumentSearchResponse.from_dict(document_search_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


