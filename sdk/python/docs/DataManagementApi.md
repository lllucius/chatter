# chatter_sdk.DataManagementApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**bulk_delete_conversations_api_v1_data_bulk_delete_conversations_post**](DataManagementApi.md#bulk_delete_conversations_api_v1_data_bulk_delete_conversations_post) | **POST** /api/v1/data/bulk/delete-conversations | Bulk Delete Conversations
[**bulk_delete_documents_api_v1_data_bulk_delete_documents_post**](DataManagementApi.md#bulk_delete_documents_api_v1_data_bulk_delete_documents_post) | **POST** /api/v1/data/bulk/delete-documents | Bulk Delete Documents
[**bulk_delete_prompts_api_v1_data_bulk_delete_prompts_post**](DataManagementApi.md#bulk_delete_prompts_api_v1_data_bulk_delete_prompts_post) | **POST** /api/v1/data/bulk/delete-prompts | Bulk Delete Prompts
[**create_backup_api_v1_data_backup_post**](DataManagementApi.md#create_backup_api_v1_data_backup_post) | **POST** /api/v1/data/backup | Create Backup
[**export_data_api_v1_data_export_post**](DataManagementApi.md#export_data_api_v1_data_export_post) | **POST** /api/v1/data/export | Export Data
[**get_storage_stats_api_v1_data_stats_get**](DataManagementApi.md#get_storage_stats_api_v1_data_stats_get) | **GET** /api/v1/data/stats | Get Storage Stats
[**list_backups_api_v1_data_backups_get**](DataManagementApi.md#list_backups_api_v1_data_backups_get) | **GET** /api/v1/data/backups | List Backups
[**restore_from_backup_api_v1_data_restore_post**](DataManagementApi.md#restore_from_backup_api_v1_data_restore_post) | **POST** /api/v1/data/restore | Restore From Backup


# **bulk_delete_conversations_api_v1_data_bulk_delete_conversations_post**
> BulkDeleteResponse bulk_delete_conversations_api_v1_data_bulk_delete_conversations_post(request_body)

Bulk Delete Conversations

Bulk delete conversations.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.bulk_delete_response import BulkDeleteResponse
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
    api_instance = chatter_sdk.DataManagementApi(api_client)
    request_body = ['request_body_example'] # List[str] | 

    try:
        # Bulk Delete Conversations
        api_response = await api_instance.bulk_delete_conversations_api_v1_data_bulk_delete_conversations_post(request_body)
        print("The response of DataManagementApi->bulk_delete_conversations_api_v1_data_bulk_delete_conversations_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataManagementApi->bulk_delete_conversations_api_v1_data_bulk_delete_conversations_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**List[str]**](str.md)|  | 

### Return type

[**BulkDeleteResponse**](BulkDeleteResponse.md)

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

# **bulk_delete_documents_api_v1_data_bulk_delete_documents_post**
> BulkDeleteResponse bulk_delete_documents_api_v1_data_bulk_delete_documents_post(request_body)

Bulk Delete Documents

Bulk delete documents.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.bulk_delete_response import BulkDeleteResponse
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
    api_instance = chatter_sdk.DataManagementApi(api_client)
    request_body = ['request_body_example'] # List[str] | 

    try:
        # Bulk Delete Documents
        api_response = await api_instance.bulk_delete_documents_api_v1_data_bulk_delete_documents_post(request_body)
        print("The response of DataManagementApi->bulk_delete_documents_api_v1_data_bulk_delete_documents_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataManagementApi->bulk_delete_documents_api_v1_data_bulk_delete_documents_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**List[str]**](str.md)|  | 

### Return type

[**BulkDeleteResponse**](BulkDeleteResponse.md)

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

# **bulk_delete_prompts_api_v1_data_bulk_delete_prompts_post**
> BulkDeleteResponse bulk_delete_prompts_api_v1_data_bulk_delete_prompts_post(request_body)

Bulk Delete Prompts

Bulk delete prompts.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.bulk_delete_response import BulkDeleteResponse
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
    api_instance = chatter_sdk.DataManagementApi(api_client)
    request_body = ['request_body_example'] # List[str] | 

    try:
        # Bulk Delete Prompts
        api_response = await api_instance.bulk_delete_prompts_api_v1_data_bulk_delete_prompts_post(request_body)
        print("The response of DataManagementApi->bulk_delete_prompts_api_v1_data_bulk_delete_prompts_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataManagementApi->bulk_delete_prompts_api_v1_data_bulk_delete_prompts_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**List[str]**](str.md)|  | 

### Return type

[**BulkDeleteResponse**](BulkDeleteResponse.md)

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

# **create_backup_api_v1_data_backup_post**
> BackupResponse create_backup_api_v1_data_backup_post(backup_request)

Create Backup

Create a data backup.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.backup_request import BackupRequest
from chatter_sdk.models.backup_response import BackupResponse
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
    api_instance = chatter_sdk.DataManagementApi(api_client)
    backup_request = chatter_sdk.BackupRequest() # BackupRequest | 

    try:
        # Create Backup
        api_response = await api_instance.create_backup_api_v1_data_backup_post(backup_request)
        print("The response of DataManagementApi->create_backup_api_v1_data_backup_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataManagementApi->create_backup_api_v1_data_backup_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **backup_request** | [**BackupRequest**](BackupRequest.md)|  | 

### Return type

[**BackupResponse**](BackupResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **export_data_api_v1_data_export_post**
> ExportDataResponse export_data_api_v1_data_export_post(export_data_request)

Export Data

Export data in specified format.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.export_data_request import ExportDataRequest
from chatter_sdk.models.export_data_response import ExportDataResponse
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
    api_instance = chatter_sdk.DataManagementApi(api_client)
    export_data_request = chatter_sdk.ExportDataRequest() # ExportDataRequest | 

    try:
        # Export Data
        api_response = await api_instance.export_data_api_v1_data_export_post(export_data_request)
        print("The response of DataManagementApi->export_data_api_v1_data_export_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataManagementApi->export_data_api_v1_data_export_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **export_data_request** | [**ExportDataRequest**](ExportDataRequest.md)|  | 

### Return type

[**ExportDataResponse**](ExportDataResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_storage_stats_api_v1_data_stats_get**
> StorageStatsResponse get_storage_stats_api_v1_data_stats_get()

Get Storage Stats

Get storage statistics and usage information.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.storage_stats_response import StorageStatsResponse
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
    api_instance = chatter_sdk.DataManagementApi(api_client)

    try:
        # Get Storage Stats
        api_response = await api_instance.get_storage_stats_api_v1_data_stats_get()
        print("The response of DataManagementApi->get_storage_stats_api_v1_data_stats_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataManagementApi->get_storage_stats_api_v1_data_stats_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**StorageStatsResponse**](StorageStatsResponse.md)

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

# **list_backups_api_v1_data_backups_get**
> BackupListResponse list_backups_api_v1_data_backups_get(backup_type=backup_type, status=status)

List Backups

List available backups.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.backup_list_response import BackupListResponse
from chatter_sdk.models.backup_type import BackupType
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
    api_instance = chatter_sdk.DataManagementApi(api_client)
    backup_type = chatter_sdk.BackupType() # BackupType |  (optional)
    status = 'status_example' # str |  (optional)

    try:
        # List Backups
        api_response = await api_instance.list_backups_api_v1_data_backups_get(backup_type=backup_type, status=status)
        print("The response of DataManagementApi->list_backups_api_v1_data_backups_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataManagementApi->list_backups_api_v1_data_backups_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **backup_type** | [**BackupType**](.md)|  | [optional] 
 **status** | **str**|  | [optional] 

### Return type

[**BackupListResponse**](BackupListResponse.md)

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

# **restore_from_backup_api_v1_data_restore_post**
> RestoreResponse restore_from_backup_api_v1_data_restore_post(restore_request)

Restore From Backup

Restore data from a backup.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.restore_request import RestoreRequest
from chatter_sdk.models.restore_response import RestoreResponse
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
    api_instance = chatter_sdk.DataManagementApi(api_client)
    restore_request = chatter_sdk.RestoreRequest() # RestoreRequest | 

    try:
        # Restore From Backup
        api_response = await api_instance.restore_from_backup_api_v1_data_restore_post(restore_request)
        print("The response of DataManagementApi->restore_from_backup_api_v1_data_restore_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DataManagementApi->restore_from_backup_api_v1_data_restore_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **restore_request** | [**RestoreRequest**](RestoreRequest.md)|  | 

### Return type

[**RestoreResponse**](RestoreResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

