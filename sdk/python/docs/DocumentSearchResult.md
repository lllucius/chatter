# DocumentSearchResult

Schema for document search result.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **str** | Document ID | 
**chunk_id** | **str** | Chunk ID | 
**score** | **float** | Similarity score | 
**content** | **str** | Matching content | 
**metadata** | **Dict[str, object]** |  | [optional] 
**document** | [**DocumentResponse**](DocumentResponse.md) |  | 

## Example

```python
from chatter_sdk.models.document_search_result import DocumentSearchResult

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentSearchResult from a JSON string
document_search_result_instance = DocumentSearchResult.from_json(json)
# print the JSON string representation of the object
print(DocumentSearchResult.to_json())

# convert the object into a dict
document_search_result_dict = document_search_result_instance.to_dict()
# create an instance of DocumentSearchResult from a dict
document_search_result_from_dict = DocumentSearchResult.from_dict(document_search_result_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


