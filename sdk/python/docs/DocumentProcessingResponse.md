# DocumentProcessingResponse

Schema for document processing response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**document_id** | **str** | Document ID | 
**status** | [**DocumentStatus**](DocumentStatus.md) |  | 
**message** | **str** | Status message | 
**processing_started_at** | **datetime** |  | [optional] 

## Example

```python
from chatter_sdk.models.document_processing_response import DocumentProcessingResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentProcessingResponse from a JSON string
document_processing_response_instance = DocumentProcessingResponse.from_json(json)
# print the JSON string representation of the object
print(DocumentProcessingResponse.to_json())

# convert the object into a dict
document_processing_response_dict = document_processing_response_instance.to_dict()
# create an instance of DocumentProcessingResponse from a dict
document_processing_response_from_dict = DocumentProcessingResponse.from_dict(document_processing_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


