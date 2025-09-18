# chatter_sdk.DocumentsApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_document_api_v1_documents_document_id_delete**](DocumentsApi.md#delete_document_api_v1_documents_document_id_delete) | **DELETE** /api/v1/documents/{document_id} | Delete Document
[**delete_document_api_v1_documents_document_id_delete_0**](DocumentsApi.md#delete_document_api_v1_documents_document_id_delete_0) | **DELETE** /api/v1/documents/{document_id} | Delete Document
[**get_document_api_v1_documents_document_id_get**](DocumentsApi.md#get_document_api_v1_documents_document_id_get) | **GET** /api/v1/documents/{document_id} | Get Document
[**get_document_api_v1_documents_document_id_get_0**](DocumentsApi.md#get_document_api_v1_documents_document_id_get_0) | **GET** /api/v1/documents/{document_id} | Get Document
[**get_user_document_stats_api_v1_documents_stats_user_get**](DocumentsApi.md#get_user_document_stats_api_v1_documents_stats_user_get) | **GET** /api/v1/documents/stats/user | Get User Document Stats
[**get_user_document_stats_api_v1_documents_stats_user_get_0**](DocumentsApi.md#get_user_document_stats_api_v1_documents_stats_user_get_0) | **GET** /api/v1/documents/stats/user | Get User Document Stats
[**list_documents_get_api_v1_documents_get**](DocumentsApi.md#list_documents_get_api_v1_documents_get) | **GET** /api/v1/documents | List Documents Get
[**list_documents_get_api_v1_documents_get_0**](DocumentsApi.md#list_documents_get_api_v1_documents_get_0) | **GET** /api/v1/documents | List Documents Get
[**list_documents_post_api_v1_documents_list_post**](DocumentsApi.md#list_documents_post_api_v1_documents_list_post) | **POST** /api/v1/documents/list | List Documents Post
[**list_documents_post_api_v1_documents_list_post_0**](DocumentsApi.md#list_documents_post_api_v1_documents_list_post_0) | **POST** /api/v1/documents/list | List Documents Post
[**reprocess_document_api_v1_documents_document_id_reprocess_post**](DocumentsApi.md#reprocess_document_api_v1_documents_document_id_reprocess_post) | **POST** /api/v1/documents/{document_id}/reprocess | Reprocess Document
[**reprocess_document_api_v1_documents_document_id_reprocess_post_0**](DocumentsApi.md#reprocess_document_api_v1_documents_document_id_reprocess_post_0) | **POST** /api/v1/documents/{document_id}/reprocess | Reprocess Document
[**search_documents_api_v1_documents_search_post**](DocumentsApi.md#search_documents_api_v1_documents_search_post) | **POST** /api/v1/documents/search | Search Documents
[**search_documents_api_v1_documents_search_post_0**](DocumentsApi.md#search_documents_api_v1_documents_search_post_0) | **POST** /api/v1/documents/search | Search Documents
[**upload_document_api_v1_documents_upload_post**](DocumentsApi.md#upload_document_api_v1_documents_upload_post) | **POST** /api/v1/documents/upload | Upload Document
[**upload_document_api_v1_documents_upload_post_0**](DocumentsApi.md#upload_document_api_v1_documents_upload_post_0) | **POST** /api/v1/documents/upload | Upload Document


# **delete_document_api_v1_documents_document_id_delete**
> Dict[str, str] delete_document_api_v1_documents_document_id_delete(document_id)

Delete Document

Delete a document.

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

**Dict[str, str]**

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

# **delete_document_api_v1_documents_document_id_delete_0**
> Dict[str, str] delete_document_api_v1_documents_document_id_delete_0(document_id)

Delete Document

Delete a document.

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
        # Delete Document
        api_response = await api_instance.delete_document_api_v1_documents_document_id_delete_0(document_id)
        print("The response of DocumentsApi->delete_document_api_v1_documents_document_id_delete_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->delete_document_api_v1_documents_document_id_delete_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  | 

### Return type

**Dict[str, str]**

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

Get a document by ID.

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
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_document_api_v1_documents_document_id_get_0**
> DocumentResponse get_document_api_v1_documents_document_id_get_0(document_id)

Get Document

Get a document by ID.

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
        api_response = await api_instance.get_document_api_v1_documents_document_id_get_0(document_id)
        print("The response of DocumentsApi->get_document_api_v1_documents_document_id_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->get_document_api_v1_documents_document_id_get_0: %s\n" % e)
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
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_user_document_stats_api_v1_documents_stats_user_get**
> DocumentStatsResponse get_user_document_stats_api_v1_documents_stats_user_get()

Get User Document Stats

Get document statistics for the current user.

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
        # Get User Document Stats
        api_response = await api_instance.get_user_document_stats_api_v1_documents_stats_user_get()
        print("The response of DocumentsApi->get_user_document_stats_api_v1_documents_stats_user_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->get_user_document_stats_api_v1_documents_stats_user_get: %s\n" % e)
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

# **get_user_document_stats_api_v1_documents_stats_user_get_0**
> DocumentStatsResponse get_user_document_stats_api_v1_documents_stats_user_get_0()

Get User Document Stats

Get document statistics for the current user.

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
        # Get User Document Stats
        api_response = await api_instance.get_user_document_stats_api_v1_documents_stats_user_get_0()
        print("The response of DocumentsApi->get_user_document_stats_api_v1_documents_stats_user_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->get_user_document_stats_api_v1_documents_stats_user_get_0: %s\n" % e)
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

# **list_documents_get_api_v1_documents_get**
> Dict[str, object] list_documents_get_api_v1_documents_get(limit=limit, offset=offset)

List Documents Get

List documents with pagination (GET endpoint for frontend compatibility).

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
    limit = 10 # int |  (optional) (default to 10)
    offset = 0 # int |  (optional) (default to 0)

    try:
        # List Documents Get
        api_response = await api_instance.list_documents_get_api_v1_documents_get(limit=limit, offset=offset)
        print("The response of DocumentsApi->list_documents_get_api_v1_documents_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->list_documents_get_api_v1_documents_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 10]
 **offset** | **int**|  | [optional] [default to 0]

### Return type

**Dict[str, object]**

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

# **list_documents_get_api_v1_documents_get_0**
> Dict[str, object] list_documents_get_api_v1_documents_get_0(limit=limit, offset=offset)

List Documents Get

List documents with pagination (GET endpoint for frontend compatibility).

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
    limit = 10 # int |  (optional) (default to 10)
    offset = 0 # int |  (optional) (default to 0)

    try:
        # List Documents Get
        api_response = await api_instance.list_documents_get_api_v1_documents_get_0(limit=limit, offset=offset)
        print("The response of DocumentsApi->list_documents_get_api_v1_documents_get_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->list_documents_get_api_v1_documents_get_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 10]
 **offset** | **int**|  | [optional] [default to 0]

### Return type

**Dict[str, object]**

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

# **list_documents_post_api_v1_documents_list_post**
> Dict[str, object] list_documents_post_api_v1_documents_list_post(document_list_request)

List Documents Post

List documents with filtering and pagination (POST endpoint for advanced filtering).

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.document_list_request import DocumentListRequest
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
    document_list_request = chatter_sdk.DocumentListRequest() # DocumentListRequest | 

    try:
        # List Documents Post
        api_response = await api_instance.list_documents_post_api_v1_documents_list_post(document_list_request)
        print("The response of DocumentsApi->list_documents_post_api_v1_documents_list_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->list_documents_post_api_v1_documents_list_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_list_request** | [**DocumentListRequest**](DocumentListRequest.md)|  | 

### Return type

**Dict[str, object]**

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

# **list_documents_post_api_v1_documents_list_post_0**
> Dict[str, object] list_documents_post_api_v1_documents_list_post_0(document_list_request)

List Documents Post

List documents with filtering and pagination (POST endpoint for advanced filtering).

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.document_list_request import DocumentListRequest
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
    document_list_request = chatter_sdk.DocumentListRequest() # DocumentListRequest | 

    try:
        # List Documents Post
        api_response = await api_instance.list_documents_post_api_v1_documents_list_post_0(document_list_request)
        print("The response of DocumentsApi->list_documents_post_api_v1_documents_list_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->list_documents_post_api_v1_documents_list_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_list_request** | [**DocumentListRequest**](DocumentListRequest.md)|  | 

### Return type

**Dict[str, object]**

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
> Dict[str, str] reprocess_document_api_v1_documents_document_id_reprocess_post(document_id)

Reprocess Document

Reprocess a document through the embedding pipeline.

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

**Dict[str, str]**

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

# **reprocess_document_api_v1_documents_document_id_reprocess_post_0**
> Dict[str, str] reprocess_document_api_v1_documents_document_id_reprocess_post_0(document_id)

Reprocess Document

Reprocess a document through the embedding pipeline.

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
        # Reprocess Document
        api_response = await api_instance.reprocess_document_api_v1_documents_document_id_reprocess_post_0(document_id)
        print("The response of DocumentsApi->reprocess_document_api_v1_documents_document_id_reprocess_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->reprocess_document_api_v1_documents_document_id_reprocess_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_id** | **str**|  | 

### Return type

**Dict[str, str]**

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
> List[SearchResultResponse] search_documents_api_v1_documents_search_post(document_search_request)

Search Documents

Search documents using semantic similarity.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.document_search_request import DocumentSearchRequest
from chatter_sdk.models.search_result_response import SearchResultResponse
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

[**List[SearchResultResponse]**](SearchResultResponse.md)

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

# **search_documents_api_v1_documents_search_post_0**
> List[SearchResultResponse] search_documents_api_v1_documents_search_post_0(document_search_request)

Search Documents

Search documents using semantic similarity.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.document_search_request import DocumentSearchRequest
from chatter_sdk.models.search_result_response import SearchResultResponse
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
        api_response = await api_instance.search_documents_api_v1_documents_search_post_0(document_search_request)
        print("The response of DocumentsApi->search_documents_api_v1_documents_search_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->search_documents_api_v1_documents_search_post_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **document_search_request** | [**DocumentSearchRequest**](DocumentSearchRequest.md)|  | 

### Return type

[**List[SearchResultResponse]**](SearchResultResponse.md)

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

Upload and process a new document.

This endpoint uploads a file, creates a document record, and starts
the embedding processing pipeline asynchronously.

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
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upload_document_api_v1_documents_upload_post_0**
> DocumentResponse upload_document_api_v1_documents_upload_post_0(file, title=title, description=description, tags=tags, chunk_size=chunk_size, chunk_overlap=chunk_overlap, is_public=is_public)

Upload Document

Upload and process a new document.

This endpoint uploads a file, creates a document record, and starts
the embedding processing pipeline asynchronously.

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
        api_response = await api_instance.upload_document_api_v1_documents_upload_post_0(file, title=title, description=description, tags=tags, chunk_size=chunk_size, chunk_overlap=chunk_overlap, is_public=is_public)
        print("The response of DocumentsApi->upload_document_api_v1_documents_upload_post_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DocumentsApi->upload_document_api_v1_documents_upload_post_0: %s\n" % e)
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
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

