# chatter_sdk.JobsApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cancel_job_api_v1_jobs_job_id_cancel_post**](JobsApi.md#cancel_job_api_v1_jobs_job_id_cancel_post) | **POST** /api/v1/jobs/{job_id}/cancel | Cancel Job
[**cleanup_jobs_api_v1_jobs_cleanup_post**](JobsApi.md#cleanup_jobs_api_v1_jobs_cleanup_post) | **POST** /api/v1/jobs/cleanup | Cleanup Jobs
[**create_job_api_v1_jobs_post**](JobsApi.md#create_job_api_v1_jobs_post) | **POST** /api/v1/jobs/ | Create Job
[**get_job_api_v1_jobs_job_id_get**](JobsApi.md#get_job_api_v1_jobs_job_id_get) | **GET** /api/v1/jobs/{job_id} | Get Job
[**get_job_stats_api_v1_jobs_stats_overview_get**](JobsApi.md#get_job_stats_api_v1_jobs_stats_overview_get) | **GET** /api/v1/jobs/stats/overview | Get Job Stats
[**list_jobs_api_v1_jobs_get**](JobsApi.md#list_jobs_api_v1_jobs_get) | **GET** /api/v1/jobs/ | List Jobs


# **cancel_job_api_v1_jobs_job_id_cancel_post**
> JobActionResponse cancel_job_api_v1_jobs_job_id_cancel_post(job_id)

Cancel Job

Cancel a job.

Args:
    job_id: Job ID
    current_user: Current authenticated user

Returns:
    Cancellation result

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.job_action_response import JobActionResponse
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
    api_instance = chatter_sdk.JobsApi(api_client)
    job_id = 'job_id_example' # str | 

    try:
        # Cancel Job
        api_response = await api_instance.cancel_job_api_v1_jobs_job_id_cancel_post(job_id)
        print("The response of JobsApi->cancel_job_api_v1_jobs_job_id_cancel_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling JobsApi->cancel_job_api_v1_jobs_job_id_cancel_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 

### Return type

[**JobActionResponse**](JobActionResponse.md)

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

# **cleanup_jobs_api_v1_jobs_cleanup_post**
> Dict[str, object] cleanup_jobs_api_v1_jobs_cleanup_post(force=force)

Cleanup Jobs

Clean up old completed jobs to free up memory.

Note: This is a system-wide cleanup operation that affects all users.
Only completed, failed, or cancelled jobs older than 24 hours are removed.

Args:
    force: If True, remove all completed/failed jobs regardless of age
    current_user: Current authenticated user

Returns:
    Cleanup statistics

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
    api_instance = chatter_sdk.JobsApi(api_client)
    force = False # bool |  (optional) (default to False)

    try:
        # Cleanup Jobs
        api_response = await api_instance.cleanup_jobs_api_v1_jobs_cleanup_post(force=force)
        print("The response of JobsApi->cleanup_jobs_api_v1_jobs_cleanup_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling JobsApi->cleanup_jobs_api_v1_jobs_cleanup_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **force** | **bool**|  | [optional] [default to False]

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

# **create_job_api_v1_jobs_post**
> JobResponse create_job_api_v1_jobs_post(job_create_request)

Create Job

Create a new job.

Args:
    job_data: Job creation data
    current_user: Current authenticated user

Returns:
    Created job data

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.job_create_request import JobCreateRequest
from chatter_sdk.models.job_response import JobResponse
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
    api_instance = chatter_sdk.JobsApi(api_client)
    job_create_request = chatter_sdk.JobCreateRequest() # JobCreateRequest | 

    try:
        # Create Job
        api_response = await api_instance.create_job_api_v1_jobs_post(job_create_request)
        print("The response of JobsApi->create_job_api_v1_jobs_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling JobsApi->create_job_api_v1_jobs_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_create_request** | [**JobCreateRequest**](JobCreateRequest.md)|  | 

### Return type

[**JobResponse**](JobResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_job_api_v1_jobs_job_id_get**
> JobResponse get_job_api_v1_jobs_job_id_get(job_id)

Get Job

Get job by ID.

Args:
    job_id: Job ID
    current_user: Current authenticated user

Returns:
    Job data

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.job_response import JobResponse
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
    api_instance = chatter_sdk.JobsApi(api_client)
    job_id = 'job_id_example' # str | 

    try:
        # Get Job
        api_response = await api_instance.get_job_api_v1_jobs_job_id_get(job_id)
        print("The response of JobsApi->get_job_api_v1_jobs_job_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling JobsApi->get_job_api_v1_jobs_job_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **str**|  | 

### Return type

[**JobResponse**](JobResponse.md)

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

# **get_job_stats_api_v1_jobs_stats_overview_get**
> JobStatsResponse get_job_stats_api_v1_jobs_stats_overview_get()

Get Job Stats

Get job queue statistics.

Args:
    current_user: Current authenticated user

Returns:
    Job statistics

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.job_stats_response import JobStatsResponse
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
    api_instance = chatter_sdk.JobsApi(api_client)

    try:
        # Get Job Stats
        api_response = await api_instance.get_job_stats_api_v1_jobs_stats_overview_get()
        print("The response of JobsApi->get_job_stats_api_v1_jobs_stats_overview_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling JobsApi->get_job_stats_api_v1_jobs_stats_overview_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**JobStatsResponse**](JobStatsResponse.md)

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

# **list_jobs_api_v1_jobs_get**
> JobListResponse list_jobs_api_v1_jobs_get(status=status, priority=priority, function_name=function_name, created_after=created_after, created_before=created_before, tags=tags, search=search, limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order)

List Jobs

List jobs with optional filtering and pagination.

Args:
    status: Filter by status
    priority: Filter by priority
    function_name: Filter by function name
    created_after: Filter jobs created after this date
    created_before: Filter jobs created before this date
    tags: Filter by job tags (any of the provided tags)
    search: Search in job names and metadata
    limit: Maximum number of results
    offset: Number of results to skip
    sort_by: Field to sort by
    sort_order: Sort order
    current_user: Current authenticated user

Returns:
    List of jobs with pagination info

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.job_list_response import JobListResponse
from chatter_sdk.models.job_priority import JobPriority
from chatter_sdk.models.job_status import JobStatus
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
    api_instance = chatter_sdk.JobsApi(api_client)
    status = chatter_sdk.JobStatus() # JobStatus | Filter by status (optional)
    priority = chatter_sdk.JobPriority() # JobPriority | Filter by priority (optional)
    function_name = 'function_name_example' # str | Filter by function name (optional)
    created_after = '2013-10-20T19:20:30+01:00' # datetime | Filter jobs created after this date (optional)
    created_before = '2013-10-20T19:20:30+01:00' # datetime | Filter jobs created before this date (optional)
    tags = ['tags_example'] # List[str] | Filter by job tags (any of the provided tags) (optional)
    search = 'search_example' # str | Search in job names and metadata (optional)
    limit = 20 # int | Maximum number of results (optional) (default to 20)
    offset = 0 # int | Number of results to skip (optional) (default to 0)
    sort_by = 'created_at' # str | Field to sort by (optional) (default to 'created_at')
    sort_order = 'desc' # str | Sort order (optional) (default to 'desc')

    try:
        # List Jobs
        api_response = await api_instance.list_jobs_api_v1_jobs_get(status=status, priority=priority, function_name=function_name, created_after=created_after, created_before=created_before, tags=tags, search=search, limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order)
        print("The response of JobsApi->list_jobs_api_v1_jobs_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling JobsApi->list_jobs_api_v1_jobs_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **status** | [**JobStatus**](.md)| Filter by status | [optional] 
 **priority** | [**JobPriority**](.md)| Filter by priority | [optional] 
 **function_name** | **str**| Filter by function name | [optional] 
 **created_after** | **datetime**| Filter jobs created after this date | [optional] 
 **created_before** | **datetime**| Filter jobs created before this date | [optional] 
 **tags** | [**List[str]**](str.md)| Filter by job tags (any of the provided tags) | [optional] 
 **search** | **str**| Search in job names and metadata | [optional] 
 **limit** | **int**| Maximum number of results | [optional] [default to 20]
 **offset** | **int**| Number of results to skip | [optional] [default to 0]
 **sort_by** | **str**| Field to sort by | [optional] [default to &#39;created_at&#39;]
 **sort_order** | **str**| Sort order | [optional] [default to &#39;desc&#39;]

### Return type

[**JobListResponse**](JobListResponse.md)

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

