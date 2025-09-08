# chatter_sdk.DocumentsApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_document_api_v1_documents_document_id_delete**](DocumentsApi.md#delete_document_api_v1_documents_document_id_delete) | **DELETE** /api/v1/documents/{document_id} | Delete Document
[**download_document_api_v1_documents_document_id_download_get**](DocumentsApi.md#download_document_api_v1_documents_document_id_download_get) | **GET** /api/v1/documents/{document_id}/download | Download Document
[**get_document_api_v1_documents_document_id_get**](DocumentsApi.md#get_document_api_v1_documents_document_id_get) | **GET** /api/v1/documents/{document_id} | Get Document
[**get_document_chunks_api_v1_documents_document_id_chunks_get**](DocumentsApi.md#get_document_chunks_api_v1_documents_document_id_chunks_get) | **GET** /api/v1/documents/{document_id}/chunks | Get Document Chunks
[**get_document_stats_api_v1_documents_stats_overview_get**](DocumentsApi.md#get_document_stats_api_v1_documents_stats_overview_get) | **GET** /api/v1/documents/stats/overview | Get Document Stats
[**list_documents_api_v1_documents_get**](DocumentsApi.md#list_documents_api_v1_documents_get) | **GET** /api/v1/documents | List Documents
[**process_document_api_v1_documents_document_id_process_post**](DocumentsApi.md#process_document_api_v1_documents_document_id_process_post) | **POST** /api/v1/documents/{document_id}/process | Process Document
[**reprocess_document_api_v1_documents_document_id_reprocess_post**](DocumentsApi.md#reprocess_document_api_v1_documents_document_id_reprocess_post) | **POST** /api/v1/documents/{document_id}/reprocess | Reprocess Document
[**search_documents_api_v1_documents_search_post**](DocumentsApi.md#search_documents_api_v1_documents_search_post) | **POST** /api/v1/documents/search | Search Documents
[**update_document_api_v1_documents_document_id_put**](DocumentsApi.md#update_document_api_v1_documents_document_id_put) | **PUT** /api/v1/documents/{document_id} | Update Document
[**upload_document_api_v1_documents_upload_post**](DocumentsApi.md#upload_document_api_v1_documents_upload_post) | **POST** /api/v1/documents/upload | Upload Document


# **delete_document_api_v1_documents_document_id_delete**
> DocumentDeleteResponse delete_document_api_v1_documents_document_id_delete(document_id)

Delete Document

Delete document.

Args:
    document_id: Document ID
    request: Delete request parameters
    current_user: Current authenticated user
    document_service: Document service

Returns:
    Success message

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.document_delete_response import DocumentDeleteResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.DocumentsApi(api_client)
    document_id = 'document_id_example' # str | 

    try:
        # Delete Document
        api_response = await api_instance.delete_document_api_v1_documents_document_id_delete(document_id)
        print("The response of DocumentsApi->delete_document_api_v1_documents_document_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->delete_document_api_v1_documents_document_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  | 

### Return type

[**DocumentDeleteResponse**](DocumentDeleteResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **download_document_api_v1_documents_document_id_download_get**
> object download_document_api_v1_documents_document_id_download_get(document_id)

Download Document

Download original document file.

Args:
    document_id: Document ID
    current_user: Current authenticated user
    document_service: Document service

Returns:
    File download response

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.DocumentsApi(api_client)
    document_id = 'document_id_example' # str | 

    try:
        # Download Document
        api_response = await api_instance.download_document_api_v1_documents_document_id_download_get(document_id)
        print("The response of DocumentsApi->download_document_api_v1_documents_document_id_download_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->download_document_api_v1_documents_document_id_download_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  | 

### Return type

**object**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_document_api_v1_documents_document_id_get**
> DocumentResponse get_document_api_v1_documents_document_id_get(document_id)

Get Document

Get document details.

Args:
    document_id: Document ID
    current_user: Current authenticated user
    document_service: Document service

Returns:
    Document information

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.document_response import DocumentResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.DocumentsApi(api_client)
    document_id = 'document_id_example' # str | 

    try:
        # Get Document
        api_response = await api_instance.get_document_api_v1_documents_document_id_get(document_id)
        print("The response of DocumentsApi->get_document_api_v1_documents_document_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->get_document_api_v1_documents_document_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  | 

### Return type

[**DocumentResponse**](DocumentResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**401** | Unauthorized - Invalid or missing authentication token |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**403** | Forbidden - User lacks permission to access this document |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**404** | Not Found - Document does not exist |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_document_chunks_api_v1_documents_document_id_chunks_get**
> DocumentChunksResponse get_document_chunks_api_v1_documents_document_id_chunks_get(document_id, limit=limit, offset=offset)

Get Document Chunks

Get document chunks.

Args:
    document_id: Document ID
    limit: Maximum number of results
    offset: Number of results to skip
    current_user: Current authenticated user
    document_service: Document service

Returns:
    List of document chunks with pagination

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.document_chunks_response import DocumentChunksResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.DocumentsApi(api_client)
    document_id = 'document_id_example' # str | 
    limit = 50 # int | Maximum number of results (optional) (default to 50)
    offset = 0 # int | Number of results to skip (optional) (default to 0)

    try:
        # Get Document Chunks
        api_response = await api_instance.get_document_chunks_api_v1_documents_document_id_chunks_get(document_id, limit=limit, offset=offset)
        print("The response of DocumentsApi->get_document_chunks_api_v1_documents_document_id_chunks_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->get_document_chunks_api_v1_documents_document_id_chunks_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  | 
 **limit** | **int**| Maximum number of results | [optional] [default to 50]
 **offset** | **int**| Number of results to skip | [optional] [default to 0]

### Return type

[**DocumentChunksResponse**](DocumentChunksResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_document_stats_api_v1_documents_stats_overview_get**
> DocumentStatsResponse get_document_stats_api_v1_documents_stats_overview_get()

Get Document Stats

Get document statistics.

Args:
    current_user: Current authenticated user
    document_service: Document service

Returns:
    Document statistics

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.document_stats_response import DocumentStatsResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.DocumentsApi(api_client)

    try:
        # Get Document Stats
        api_response = await api_instance.get_document_stats_api_v1_documents_stats_overview_get()
        print("The response of DocumentsApi->get_document_stats_api_v1_documents_stats_overview_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->get_document_stats_api_v1_documents_stats_overview_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**DocumentStatsResponse**](DocumentStatsResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_documents_api_v1_documents_get**
> DocumentListResponse list_documents_api_v1_documents_get(status=status, document_type=document_type, tags=tags, owner_id=owner_id, limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order)

List Documents

List user's documents.

Args:
    status: Filter by document status
    document_type: Filter by document type
    tags: Filter by tags
    owner_id: Filter by owner (admin only)
    limit: Maximum number of results
    offset: Number of results to skip
    sort_by: Sort field
    sort_order: Sort order (asc/desc)
    current_user: Current authenticated user
    document_service: Document service

Returns:
    List of documents with pagination info

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.document_list_response import DocumentListResponse
from chatter_sdk.models.document_status import DocumentStatus
from chatter_sdk.models.document_type import DocumentType
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.DocumentsApi(api_client)
    status = chatter_sdk.DocumentStatus() # DocumentStatus | Filter by status (optional)
    document_type = chatter_sdk.DocumentType() # DocumentType | Filter by document type (optional)
    tags = ['tags_example'] # List[str] | Filter by tags (optional)
    owner_id = 'owner_id_example' # str | Filter by owner (admin only) (optional)
    limit = 50 # int | Maximum number of results (optional) (default to 50)
    offset = 0 # int | Number of results to skip (optional) (default to 0)
    sort_by = 'created_at' # str | Sort field (optional) (default to 'created_at')
    sort_order = 'desc' # str | Sort order (optional) (default to 'desc')

    try:
        # List Documents
        api_response = await api_instance.list_documents_api_v1_documents_get(status=status, document_type=document_type, tags=tags, owner_id=owner_id, limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order)
        print("The response of DocumentsApi->list_documents_api_v1_documents_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->list_documents_api_v1_documents_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **status** | [**DocumentStatus**](.md)| Filter by status | [optional] 
 **document_type** | [**DocumentType**](.md)| Filter by document type | [optional] 
 **tags** | [**List[str]**](str.md)| Filter by tags | [optional] 
 **owner_id** | **str**| Filter by owner (admin only) | [optional] 
 **limit** | **int**| Maximum number of results | [optional] [default to 50]
 **offset** | **int**| Number of results to skip | [optional] [default to 0]
 **sort_by** | **str**| Sort field | [optional] [default to &#39;created_at&#39;]
 **sort_order** | **str**| Sort order | [optional] [default to &#39;desc&#39;]

### Return type

[**DocumentListResponse**](DocumentListResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**401** | Unauthorized - Invalid or missing authentication token |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**403** | Forbidden - User lacks permission to access documents |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **process_document_api_v1_documents_document_id_process_post**
> DocumentProcessingResponse process_document_api_v1_documents_document_id_process_post(document_id, document_processing_request)

Process Document

Trigger document processing.

Args:
    document_id: Document ID
    processing_request: Processing request
    current_user: Current authenticated user
    document_service: Document service

Returns:
    Processing status

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.document_processing_request import DocumentProcessingRequest
from chatter_sdk.models.document_processing_response import DocumentProcessingResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.DocumentsApi(api_client)
    document_id = 'document_id_example' # str | 
    document_processing_request = chatter_sdk.DocumentProcessingRequest() # DocumentProcessingRequest | 

    try:
        # Process Document
        api_response = await api_instance.process_document_api_v1_documents_document_id_process_post(document_id, document_processing_request)
        print("The response of DocumentsApi->process_document_api_v1_documents_document_id_process_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->process_document_api_v1_documents_document_id_process_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  | 
 **document_processing_request** | [**DocumentProcessingRequest**](DocumentProcessingRequest.md)|  | 

### Return type

[**DocumentProcessingResponse**](DocumentProcessingResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reprocess_document_api_v1_documents_document_id_reprocess_post**
> DocumentProcessingResponse reprocess_document_api_v1_documents_document_id_reprocess_post(document_id)

Reprocess Document

Reprocess an existing document.

Args:
    document_id: Document ID
    current_user: Current authenticated user
    document_service: Document service

Returns:
    Processing status

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.document_processing_response import DocumentProcessingResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.DocumentsApi(api_client)
    document_id = 'document_id_example' # str | 

    try:
        # Reprocess Document
        api_response = await api_instance.reprocess_document_api_v1_documents_document_id_reprocess_post(document_id)
        print("The response of DocumentsApi->reprocess_document_api_v1_documents_document_id_reprocess_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->reprocess_document_api_v1_documents_document_id_reprocess_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  | 

### Return type

[**DocumentProcessingResponse**](DocumentProcessingResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_documents_api_v1_documents_search_post**
> DocumentSearchResponse search_documents_api_v1_documents_search_post(document_search_request)

Search Documents

Search documents using vector similarity.

Args:
    search_request: Search request
    current_user: Current authenticated user
    document_service: Document service

Returns:
    Search results

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.document_search_request import DocumentSearchRequest
from chatter_sdk.models.document_search_response import DocumentSearchResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.DocumentsApi(api_client)
    document_search_request = chatter_sdk.DocumentSearchRequest() # DocumentSearchRequest | 

    try:
        # Search Documents
        api_response = await api_instance.search_documents_api_v1_documents_search_post(document_search_request)
        print("The response of DocumentsApi->search_documents_api_v1_documents_search_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->search_documents_api_v1_documents_search_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_search_request** | [**DocumentSearchRequest**](DocumentSearchRequest.md)|  | 

### Return type

[**DocumentSearchResponse**](DocumentSearchResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_document_api_v1_documents_document_id_put**
> DocumentResponse update_document_api_v1_documents_document_id_put(document_id, document_update)

Update Document

Update document metadata.

Args:
    document_id: Document ID
    update_data: Update data
    current_user: Current authenticated user
    document_service: Document service

Returns:
    Updated document information

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.document_response import DocumentResponse
from chatter_sdk.models.document_update import DocumentUpdate
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.DocumentsApi(api_client)
    document_id = 'document_id_example' # str | 
    document_update = chatter_sdk.DocumentUpdate() # DocumentUpdate | 

    try:
        # Update Document
        api_response = await api_instance.update_document_api_v1_documents_document_id_put(document_id, document_update)
        print("The response of DocumentsApi->update_document_api_v1_documents_document_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->update_document_api_v1_documents_document_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  | 
 **document_update** | [**DocumentUpdate**](DocumentUpdate.md)|  | 

### Return type

[**DocumentResponse**](DocumentResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_document_api_v1_documents_upload_post**
> DocumentResponse upload_document_api_v1_documents_upload_post(file, title=title, description=description, tags=tags, chunk_size=chunk_size, chunk_overlap=chunk_overlap, is_public=is_public)

Upload Document

Upload a document.

Args:
    file: Document file to upload
    title: Document title
    description: Document description
    tags: Document tags (JSON array string)
    chunk_size: Text chunk size for processing
    chunk_overlap: Text chunk overlap
    is_public: Whether document is public
    current_user: Current authenticated user
    document_service: Document service

Returns:
    Created document information

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.document_response import DocumentResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.DocumentsApi(api_client)
    file = None # bytearray | 
    title = 'title_example' # str |  (optional)
    description = 'description_example' # str |  (optional)
    tags = 'tags_example' # str |  (optional)
    chunk_size = 1000 # int |  (optional) (default to 1000)
    chunk_overlap = 200 # int |  (optional) (default to 200)
    is_public = False # bool |  (optional) (default to False)

    try:
        # Upload Document
        api_response = await api_instance.upload_document_api_v1_documents_upload_post(file, title=title, description=description, tags=tags, chunk_size=chunk_size, chunk_overlap=chunk_overlap, is_public=is_public)
        print("The response of DocumentsApi->upload_document_api_v1_documents_upload_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->upload_document_api_v1_documents_upload_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **bytearray**|  | 
 **title** | **str**|  | [optional] 
 **description** | **str**|  | [optional] 
 **tags** | **str**|  | [optional] 
 **chunk_size** | **int**|  | [optional] [default to 1000]
 **chunk_overlap** | **int**|  | [optional] [default to 200]
 **is_public** | **bool**|  | [optional] [default to False]

### Return type

[**DocumentResponse**](DocumentResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

