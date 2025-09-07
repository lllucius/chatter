# DocumentStatsResponse

Schema for document statistics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_documents** | **int** | Total number of documents | 
**total_chunks** | **int** | Total number of chunks | 
**total_size_bytes** | **int** | Total size in bytes | 
**documents_by_status** | **Dict[str, int]** | Documents grouped by status | 
**documents_by_type** | **Dict[str, int]** | Documents grouped by type | 
**processing_stats** | **Dict[str, object]** | Processing statistics | 

## Example

```python
from chatter_sdk.models.document_stats_response import DocumentStatsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentStatsResponse from a JSON string
document_stats_response_instance = DocumentStatsResponse.from_json(json)
# print the JSON string representation of the object
print(DocumentStatsResponse.to_json())

# convert the object into a dict
document_stats_response_dict = document_stats_response_instance.to_dict()
# create an instance of DocumentStatsResponse from a dict
document_stats_response_from_dict = DocumentStatsResponse.from_dict(document_stats_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


