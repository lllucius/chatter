# DocumentProcessingRequest

Schema for document processing request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**reprocess** | **bool** | Force reprocessing | [optional] [default to False]
**chunk_size** | **int** |  | [optional] 
**chunk_overlap** | **int** |  | [optional] 
**generate_embeddings** | **bool** | Generate embeddings for chunks | [optional] [default to True]

## Example

```python
from chatter_sdk.models.document_processing_request import DocumentProcessingRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentProcessingRequest from a JSON string
document_processing_request_instance = DocumentProcessingRequest.from_json(json)
# print the JSON string representation of the object
print(DocumentProcessingRequest.to_json())

# convert the object into a dict
document_processing_request_dict = document_processing_request_instance.to_dict()
# create an instance of DocumentProcessingRequest from a dict
document_processing_request_from_dict = DocumentProcessingRequest.from_dict(document_processing_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


