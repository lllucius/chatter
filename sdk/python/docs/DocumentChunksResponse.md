# DocumentChunksResponse

Schema for document chunks response with pagination.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**chunks** | [**List[DocumentChunkResponse]**](DocumentChunkResponse.md) | List of document chunks | 
**total_count** | **int** | Total number of chunks | 
**limit** | **int** | Applied limit | 
**offset** | **int** | Applied offset | 

## Example

```python
from chatter_sdk.models.document_chunks_response import DocumentChunksResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentChunksResponse from a JSON string
document_chunks_response_instance = DocumentChunksResponse.from_json(json)
# print the JSON string representation of the object
print(DocumentChunksResponse.to_json())

# convert the object into a dict
document_chunks_response_dict = document_chunks_response_instance.to_dict()
# create an instance of DocumentChunksResponse from a dict
document_chunks_response_from_dict = DocumentChunksResponse.from_dict(document_chunks_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


