# DocumentSearchRequest

Schema for document search request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**query** | **str** | Search query | 
**limit** | **int** | Maximum number of results | [optional] [default to 10]
**score_threshold** | **float** | Minimum similarity score | [optional] [default to 0.5]
**document_types** | [**List[DocumentType]**](DocumentType.md) |  | [optional] 
**tags** | **List[str]** |  | [optional] 
**include_content** | **bool** | Include document content in results | [optional] [default to False]

## Example

```python
from chatter_sdk.models.document_search_request import DocumentSearchRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentSearchRequest from a JSON string
document_search_request_instance = DocumentSearchRequest.from_json(json)
# print the JSON string representation of the object
print(DocumentSearchRequest.to_json())

# convert the object into a dict
document_search_request_dict = document_search_request_instance.to_dict()
# create an instance of DocumentSearchRequest from a dict
document_search_request_from_dict = DocumentSearchRequest.from_dict(document_search_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


