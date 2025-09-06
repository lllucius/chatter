# DocumentResponse

Schema for document response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**title** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**tags** | **List[str]** |  | [optional] 
**extra_metadata** | **Dict[str, object]** |  | [optional] 
**is_public** | **bool** | Whether document is public | [optional] [default to False]
**id** | **str** | Document ID | 
**owner_id** | **str** | Owner user ID | 
**filename** | **str** | Document filename | 
**original_filename** | **str** | Original filename | 
**file_size** | **int** | File size in bytes | 
**file_hash** | **str** | File hash (SHA-256) | 
**mime_type** | **str** | MIME type | 
**document_type** | [**DocumentType**](DocumentType.md) |  | 
**status** | [**DocumentStatus**](DocumentStatus.md) |  | 
**processing_started_at** | **datetime** |  | [optional] 
**processing_completed_at** | **datetime** |  | [optional] 
**processing_error** | **str** |  | [optional] 
**chunk_size** | **int** | Chunk size | 
**chunk_overlap** | **int** | Chunk overlap | 
**chunk_count** | **int** | Number of chunks | 
**version** | **int** | Document version | 
**parent_document_id** | **str** |  | [optional] 
**view_count** | **int** | View count | 
**search_count** | **int** | Search count | 
**last_accessed_at** | **datetime** |  | [optional] 
**created_at** | **datetime** | Creation time | 
**updated_at** | **datetime** | Last update time | 

## Example

```python
from chatter_sdk.models.document_response import DocumentResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentResponse from a JSON string
document_response_instance = DocumentResponse.from_json(json)
# print the JSON string representation of the object
print(DocumentResponse.to_json())

# convert the object into a dict
document_response_dict = document_response_instance.to_dict()
# create an instance of DocumentResponse from a dict
document_response_from_dict = DocumentResponse.from_dict(document_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


