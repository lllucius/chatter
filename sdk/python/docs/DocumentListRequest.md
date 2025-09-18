# DocumentListRequest

Schema for document list request.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | [**DocumentStatus**](DocumentStatus.md) |  | [optional] 
**document_type** | [**DocumentType**](DocumentType.md) |  | [optional] 
**tags** | **List[str]** |  | [optional] 
**owner_id** | **str** |  | [optional] 
**limit** | **int** | Maximum number of results | [optional] [default to 50]
**offset** | **int** | Number of results to skip | [optional] [default to 0]
**sort_by** | **str** | Sort field | [optional] [default to 'created_at']
**sort_order** | **str** | Sort order | [optional] [default to 'desc']

## Example

```python
from chatter_sdk.models.document_list_request import DocumentListRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentListRequest from a JSON string
document_list_request_instance = DocumentListRequest.from_json(json)
# print the JSON string representation of the object
print(DocumentListRequest.to_json())

# convert the object into a dict
document_list_request_dict = document_list_request_instance.to_dict()
# create an instance of DocumentListRequest from a dict
document_list_request_from_dict = DocumentListRequest.from_dict(document_list_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


