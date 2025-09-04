# JobsApi

All URIs are relative to *http://localhost:8000*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**cancelJobApiV1JobsJobIdCancelPost**](#canceljobapiv1jobsjobidcancelpost) | **POST** /api/v1/jobs/{job_id}/cancel | Cancel Job|
|[**cleanupJobsApiV1JobsCleanupPost**](#cleanupjobsapiv1jobscleanuppost) | **POST** /api/v1/jobs/cleanup | Cleanup Jobs|
|[**createJobApiV1JobsPost**](#createjobapiv1jobspost) | **POST** /api/v1/jobs/ | Create Job|
|[**getJobApiV1JobsJobIdGet**](#getjobapiv1jobsjobidget) | **GET** /api/v1/jobs/{job_id} | Get Job|
|[**getJobStatsApiV1JobsStatsOverviewGet**](#getjobstatsapiv1jobsstatsoverviewget) | **GET** /api/v1/jobs/stats/overview | Get Job Stats|
|[**listJobsApiV1JobsGet**](#listjobsapiv1jobsget) | **GET** /api/v1/jobs/ | List Jobs|

# **cancelJobApiV1JobsJobIdCancelPost**
> JobActionResponse cancelJobApiV1JobsJobIdCancelPost()

Cancel a job.  Args:     job_id: Job ID     current_user: Current authenticated user  Returns:     Cancellation result

### Example

```typescript
import {
    JobsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new JobsApi(configuration);

let jobId: string; // (default to undefined)

const { status, data } = await apiInstance.cancelJobApiV1JobsJobIdCancelPost(
    jobId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **jobId** | [**string**] |  | defaults to undefined|


### Return type

**JobActionResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **cleanupJobsApiV1JobsCleanupPost**
> { [key: string]: any; } cleanupJobsApiV1JobsCleanupPost()

Clean up old completed jobs to free up memory.  Note: This is a system-wide cleanup operation that affects all users. Only completed, failed, or cancelled jobs older than 24 hours are removed.  Args:     force: If True, remove all completed/failed jobs regardless of age     current_user: Current authenticated user      Returns:     Cleanup statistics

### Example

```typescript
import {
    JobsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new JobsApi(configuration);

let force: boolean; // (optional) (default to false)

const { status, data } = await apiInstance.cleanupJobsApiV1JobsCleanupPost(
    force
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **force** | [**boolean**] |  | (optional) defaults to false|


### Return type

**{ [key: string]: any; }**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createJobApiV1JobsPost**
> JobResponse createJobApiV1JobsPost(jobCreateRequest)

Create a new job.  Args:     job_data: Job creation data     current_user: Current authenticated user  Returns:     Created job data

### Example

```typescript
import {
    JobsApi,
    Configuration,
    JobCreateRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new JobsApi(configuration);

let jobCreateRequest: JobCreateRequest; //

const { status, data } = await apiInstance.createJobApiV1JobsPost(
    jobCreateRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **jobCreateRequest** | **JobCreateRequest**|  | |


### Return type

**JobResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getJobApiV1JobsJobIdGet**
> JobResponse getJobApiV1JobsJobIdGet()

Get job by ID.  Args:     job_id: Job ID     current_user: Current authenticated user  Returns:     Job data

### Example

```typescript
import {
    JobsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new JobsApi(configuration);

let jobId: string; // (default to undefined)

const { status, data } = await apiInstance.getJobApiV1JobsJobIdGet(
    jobId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **jobId** | [**string**] |  | defaults to undefined|


### Return type

**JobResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getJobStatsApiV1JobsStatsOverviewGet**
> JobStatsResponse getJobStatsApiV1JobsStatsOverviewGet()

Get job queue statistics.  Args:     current_user: Current authenticated user  Returns:     Job statistics

### Example

```typescript
import {
    JobsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new JobsApi(configuration);

const { status, data } = await apiInstance.getJobStatsApiV1JobsStatsOverviewGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**JobStatsResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listJobsApiV1JobsGet**
> JobListResponse listJobsApiV1JobsGet()

List jobs with optional filtering and pagination.  Args:     request: List request parameters     current_user: Current authenticated user  Returns:     List of jobs with pagination info

### Example

```typescript
import {
    JobsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new JobsApi(configuration);

let status: JobStatus; // (optional) (default to undefined)
let priority: JobPriority; // (optional) (default to undefined)
let functionName: string; // (optional) (default to undefined)
let createdAfter: string; // (optional) (default to undefined)
let createdBefore: string; // (optional) (default to undefined)
let search: string; // (optional) (default to undefined)
let limit: number; // (optional) (default to 20)
let offset: number; // (optional) (default to 0)
let sortBy: string; // (optional) (default to 'created_at')
let sortOrder: string; // (optional) (default to 'desc')
let requestBody: Array<string>; // (optional)

const { status, data } = await apiInstance.listJobsApiV1JobsGet(
    status,
    priority,
    functionName,
    createdAfter,
    createdBefore,
    search,
    limit,
    offset,
    sortBy,
    sortOrder,
    requestBody
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **Array<string>**|  | |
| **status** | **JobStatus** |  | (optional) defaults to undefined|
| **priority** | **JobPriority** |  | (optional) defaults to undefined|
| **functionName** | [**string**] |  | (optional) defaults to undefined|
| **createdAfter** | [**string**] |  | (optional) defaults to undefined|
| **createdBefore** | [**string**] |  | (optional) defaults to undefined|
| **search** | [**string**] |  | (optional) defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 20|
| **offset** | [**number**] |  | (optional) defaults to 0|
| **sortBy** | [**string**] |  | (optional) defaults to 'created_at'|
| **sortOrder** | [**string**] |  | (optional) defaults to 'desc'|


### Return type

**JobListResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

