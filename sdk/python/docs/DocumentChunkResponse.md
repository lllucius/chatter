# DocumentChunkResponse

Schema for document chunk response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** | Chunk ID | 
**document_id** | **str** | Document ID | 
**content** | **str** | Chunk content | 
**chunk_index** | **int** | Chunk index | 
**start_char** | **int** |  | [optional] 
**end_char** | **int** |  | [optional] 
**extra_metadata** | **Dict[str, object]** |  | [optional] 
**token_count** | **int** |  | [optional] 
**language** | **str** |  | [optional] 
**embedding_model** | **str** |  | [optional] 
**embedding_provider** | **str** |  | [optional] 
**embedding_created_at** | **datetime** |  | [optional] 
**content_hash** | **str** | Content hash | 
**created_at** | **datetime** | Creation time | 
**updated_at** | **datetime** | Last update time | 

## Example

```python
from chatter_sdk.models.document_chunk_response import DocumentChunkResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentChunkResponse from a JSON string
document_chunk_response_instance = DocumentChunkResponse.from_json(json)
# print the JSON string representation of the object
print(DocumentChunkResponse.to_json())

# convert the object into a dict
document_chunk_response_dict = document_chunk_response_instance.to_dict()
# create an instance of DocumentChunkResponse from a dict
document_chunk_response_from_dict = DocumentChunkResponse.from_dict(document_chunk_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


