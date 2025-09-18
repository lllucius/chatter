# SearchResultResponse

Schema for individual search result.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**chunk_id** | **str** | Chunk ID | 
**document_id** | **str** | Document ID | 
**content** | **str** | Matching content | 
**similarity_score** | **float** | Similarity score | 
**document_title** | **str** |  | [optional] 
**document_filename** | **str** | Document filename | 
**chunk_index** | **int** | Chunk index | 

## Example

```python
from chatter_sdk.models.search_result_response import SearchResultResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SearchResultResponse from a JSON string
search_result_response_instance = SearchResultResponse.from_json(json)
# print the JSON string representation of the object
print(SearchResultResponse.to_json())

# convert the object into a dict
search_result_response_dict = search_result_response_instance.to_dict()
# create an instance of SearchResultResponse from a dict
search_result_response_from_dict = SearchResultResponse.from_dict(search_result_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


