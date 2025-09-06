# DocumentAnalyticsResponse

Schema for document analytics response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**total_documents** | **int** | Total number of documents | 
**documents_by_status** | **Dict[str, int]** | Documents by processing status | 
**documents_by_type** | **Dict[str, int]** | Documents by file type | 
**avg_processing_time_seconds** | **float** | Average processing time | 
**processing_success_rate** | **float** | Processing success rate | 
**total_chunks** | **int** | Total number of chunks | 
**avg_chunks_per_document** | **float** | Average chunks per document | 
**total_storage_bytes** | **int** | Total storage used | 
**avg_document_size_bytes** | **float** | Average document size | 
**storage_by_type** | **Dict[str, int]** | Storage usage by document type | 
**total_searches** | **int** | Total number of searches | 
**avg_search_results** | **float** | Average search results returned | 
**popular_search_terms** | **Dict[str, int]** | Popular search terms | 
**total_views** | **int** | Total document views | 
**most_viewed_documents** | **List[Dict[str, object]]** | Most viewed documents | 
**documents_by_access_level** | **Dict[str, int]** | Documents by access level | 

## Example

```python
from chatter_sdk.models.document_analytics_response import DocumentAnalyticsResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DocumentAnalyticsResponse from a JSON string
document_analytics_response_instance = DocumentAnalyticsResponse.from_json(json)
# print the JSON string representation of the object
print(DocumentAnalyticsResponse.to_json())

# convert the object into a dict
document_analytics_response_dict = document_analytics_response_instance.to_dict()
# create an instance of DocumentAnalyticsResponse from a dict
document_analytics_response_from_dict = DocumentAnalyticsResponse.from_dict(document_analytics_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


