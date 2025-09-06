# AnalyticsApi

All URIs are relative to *http://localhost:8000*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**exportAnalyticsApiV1AnalyticsExportPost**](#exportanalyticsapiv1analyticsexportpost) | **POST** /api/v1/analytics/export | Export Analytics|
|[**getAnalyticsHealthApiV1AnalyticsHealthGet**](#getanalyticshealthapiv1analyticshealthget) | **GET** /api/v1/analytics/health | Get Analytics Health|
|[**getAnalyticsMetricsSummaryApiV1AnalyticsMetricsSummaryGet**](#getanalyticsmetricssummaryapiv1analyticsmetricssummaryget) | **GET** /api/v1/analytics/metrics/summary | Get Analytics Metrics Summary|
|[**getConversationStatsApiV1AnalyticsConversationsGet**](#getconversationstatsapiv1analyticsconversationsget) | **GET** /api/v1/analytics/conversations | Get Conversation Stats|
|[**getDashboardApiV1AnalyticsDashboardGet**](#getdashboardapiv1analyticsdashboardget) | **GET** /api/v1/analytics/dashboard | Get Dashboard|
|[**getDocumentAnalyticsApiV1AnalyticsDocumentsGet**](#getdocumentanalyticsapiv1analyticsdocumentsget) | **GET** /api/v1/analytics/documents | Get Document Analytics|
|[**getPerformanceMetricsApiV1AnalyticsPerformanceGet**](#getperformancemetricsapiv1analyticsperformanceget) | **GET** /api/v1/analytics/performance | Get Performance Metrics|
|[**getSystemAnalyticsApiV1AnalyticsSystemGet**](#getsystemanalyticsapiv1analyticssystemget) | **GET** /api/v1/analytics/system | Get System Analytics|
|[**getToolServerAnalyticsApiV1AnalyticsToolserversGet**](#gettoolserveranalyticsapiv1analyticstoolserversget) | **GET** /api/v1/analytics/toolservers | Get Tool Server Analytics|
|[**getUsageMetricsApiV1AnalyticsUsageGet**](#getusagemetricsapiv1analyticsusageget) | **GET** /api/v1/analytics/usage | Get Usage Metrics|
|[**getUserAnalyticsApiV1AnalyticsUsersUserIdGet**](#getuseranalyticsapiv1analyticsusersuseridget) | **GET** /api/v1/analytics/users/{user_id} | Get User Analytics|

# **exportAnalyticsApiV1AnalyticsExportPost**
> any exportAnalyticsApiV1AnalyticsExportPost()

Export analytics reports.  Args:     format: Export format     metrics: List of metrics to export     start_date: Start date for analytics     end_date: End date for analytics     period: Predefined period     current_user: Current authenticated user     analytics_service: Analytics service  Returns:     Exported analytics report

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let metrics: Array<string>; //List of metrics to export (default to undefined)
let format: string; //Export format (json, csv, xlsx) (optional) (default to 'json')
let startDate: string; //Start date for analytics (optional) (default to undefined)
let endDate: string; //End date for analytics (optional) (default to undefined)
let period: string; //Predefined period (1h, 24h, 7d, 30d, 90d) (optional) (default to '7d')

const { status, data } = await apiInstance.exportAnalyticsApiV1AnalyticsExportPost(
    metrics,
    format,
    startDate,
    endDate,
    period
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **metrics** | **Array&lt;string&gt;** | List of metrics to export | defaults to undefined|
| **format** | [**string**] | Export format (json, csv, xlsx) | (optional) defaults to 'json'|
| **startDate** | [**string**] | Start date for analytics | (optional) defaults to undefined|
| **endDate** | [**string**] | End date for analytics | (optional) defaults to undefined|
| **period** | [**string**] | Predefined period (1h, 24h, 7d, 30d, 90d) | (optional) defaults to '7d'|


### Return type

**any**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAnalyticsHealthApiV1AnalyticsHealthGet**
> { [key: string]: any; } getAnalyticsHealthApiV1AnalyticsHealthGet()

Get analytics system health status.  Returns:     Health check results for analytics system

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

const { status, data } = await apiInstance.getAnalyticsHealthApiV1AnalyticsHealthGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**{ [key: string]: any; }**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAnalyticsMetricsSummaryApiV1AnalyticsMetricsSummaryGet**
> { [key: string]: any; } getAnalyticsMetricsSummaryApiV1AnalyticsMetricsSummaryGet()

Get summary of key analytics metrics for monitoring.  Returns:     Summary of analytics metrics

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

const { status, data } = await apiInstance.getAnalyticsMetricsSummaryApiV1AnalyticsMetricsSummaryGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**{ [key: string]: any; }**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getConversationStatsApiV1AnalyticsConversationsGet**
> ConversationStatsResponse getConversationStatsApiV1AnalyticsConversationsGet()

Get conversation statistics.  Args:     start_date: Start date for analytics     end_date: End date for analytics     period: Predefined period     current_user: Current authenticated user     analytics_service: Analytics service  Returns:     Conversation statistics

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let startDate: string; //Start date for analytics (optional) (default to undefined)
let endDate: string; //End date for analytics (optional) (default to undefined)
let period: string; //Predefined period (1h, 24h, 7d, 30d, 90d) (optional) (default to '7d')

const { status, data } = await apiInstance.getConversationStatsApiV1AnalyticsConversationsGet(
    startDate,
    endDate,
    period
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **startDate** | [**string**] | Start date for analytics | (optional) defaults to undefined|
| **endDate** | [**string**] | End date for analytics | (optional) defaults to undefined|
| **period** | [**string**] | Predefined period (1h, 24h, 7d, 30d, 90d) | (optional) defaults to '7d'|


### Return type

**ConversationStatsResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getDashboardApiV1AnalyticsDashboardGet**
> DashboardResponse getDashboardApiV1AnalyticsDashboardGet()

Get comprehensive dashboard data.  Args:     request: Dashboard request parameters     current_user: Current authenticated user     analytics_service: Analytics service  Returns:     Complete dashboard data

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let startDate: string; //Start date for analytics (optional) (default to undefined)
let endDate: string; //End date for analytics (optional) (default to undefined)
let period: string; //Predefined period (1h, 24h, 7d, 30d, 90d) (optional) (default to '7d')

const { status, data } = await apiInstance.getDashboardApiV1AnalyticsDashboardGet(
    startDate,
    endDate,
    period
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **startDate** | [**string**] | Start date for analytics | (optional) defaults to undefined|
| **endDate** | [**string**] | End date for analytics | (optional) defaults to undefined|
| **period** | [**string**] | Predefined period (1h, 24h, 7d, 30d, 90d) | (optional) defaults to '7d'|


### Return type

**DashboardResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getDocumentAnalyticsApiV1AnalyticsDocumentsGet**
> DocumentAnalyticsResponse getDocumentAnalyticsApiV1AnalyticsDocumentsGet()

Get document analytics.  Args:     request: Document analytics request parameters     current_user: Current authenticated user     analytics_service: Analytics service  Returns:     Document analytics

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let startDate: string; //Start date for analytics (optional) (default to undefined)
let endDate: string; //End date for analytics (optional) (default to undefined)
let period: string; //Predefined period (1h, 24h, 7d, 30d, 90d) (optional) (default to '7d')

const { status, data } = await apiInstance.getDocumentAnalyticsApiV1AnalyticsDocumentsGet(
    startDate,
    endDate,
    period
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **startDate** | [**string**] | Start date for analytics | (optional) defaults to undefined|
| **endDate** | [**string**] | End date for analytics | (optional) defaults to undefined|
| **period** | [**string**] | Predefined period (1h, 24h, 7d, 30d, 90d) | (optional) defaults to '7d'|


### Return type

**DocumentAnalyticsResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getPerformanceMetricsApiV1AnalyticsPerformanceGet**
> PerformanceMetricsResponse getPerformanceMetricsApiV1AnalyticsPerformanceGet()

Get performance metrics.  Args:     request: Performance metrics request parameters     current_user: Current authenticated user     analytics_service: Analytics service  Returns:     Performance metrics

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let startDate: string; //Start date for analytics (optional) (default to undefined)
let endDate: string; //End date for analytics (optional) (default to undefined)
let period: string; //Predefined period (1h, 24h, 7d, 30d, 90d) (optional) (default to '7d')

const { status, data } = await apiInstance.getPerformanceMetricsApiV1AnalyticsPerformanceGet(
    startDate,
    endDate,
    period
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **startDate** | [**string**] | Start date for analytics | (optional) defaults to undefined|
| **endDate** | [**string**] | End date for analytics | (optional) defaults to undefined|
| **period** | [**string**] | Predefined period (1h, 24h, 7d, 30d, 90d) | (optional) defaults to '7d'|


### Return type

**PerformanceMetricsResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getSystemAnalyticsApiV1AnalyticsSystemGet**
> SystemAnalyticsResponse getSystemAnalyticsApiV1AnalyticsSystemGet()

Get system analytics.  Args:     request: System analytics request parameters     current_user: Current authenticated user     analytics_service: Analytics service  Returns:     System analytics

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

const { status, data } = await apiInstance.getSystemAnalyticsApiV1AnalyticsSystemGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**SystemAnalyticsResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getToolServerAnalyticsApiV1AnalyticsToolserversGet**
> { [key: string]: any; } getToolServerAnalyticsApiV1AnalyticsToolserversGet()

Get tool server analytics.  Args:     request: Tool server analytics request parameters     current_user: Current authenticated user     analytics_service: Analytics service  Returns:     Tool server analytics data

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let startDate: string; //Start date for analytics (optional) (default to undefined)
let endDate: string; //End date for analytics (optional) (default to undefined)
let period: string; //Predefined period (1h, 24h, 7d, 30d, 90d) (optional) (default to '7d')

const { status, data } = await apiInstance.getToolServerAnalyticsApiV1AnalyticsToolserversGet(
    startDate,
    endDate,
    period
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **startDate** | [**string**] | Start date for analytics | (optional) defaults to undefined|
| **endDate** | [**string**] | End date for analytics | (optional) defaults to undefined|
| **period** | [**string**] | Predefined period (1h, 24h, 7d, 30d, 90d) | (optional) defaults to '7d'|


### Return type

**{ [key: string]: any; }**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getUsageMetricsApiV1AnalyticsUsageGet**
> UsageMetricsResponse getUsageMetricsApiV1AnalyticsUsageGet()

Get usage metrics.  Args:     start_date: Start date for analytics     end_date: End date for analytics     period: Predefined period     current_user: Current authenticated user     analytics_service: Analytics service  Returns:     Usage metrics

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let startDate: string; //Start date for analytics (optional) (default to undefined)
let endDate: string; //End date for analytics (optional) (default to undefined)
let period: string; //Predefined period (1h, 24h, 7d, 30d, 90d) (optional) (default to '7d')

const { status, data } = await apiInstance.getUsageMetricsApiV1AnalyticsUsageGet(
    startDate,
    endDate,
    period
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **startDate** | [**string**] | Start date for analytics | (optional) defaults to undefined|
| **endDate** | [**string**] | End date for analytics | (optional) defaults to undefined|
| **period** | [**string**] | Predefined period (1h, 24h, 7d, 30d, 90d) | (optional) defaults to '7d'|


### Return type

**UsageMetricsResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getUserAnalyticsApiV1AnalyticsUsersUserIdGet**
> { [key: string]: any; } getUserAnalyticsApiV1AnalyticsUsersUserIdGet()

Get per-user analytics.  Args:     user_id: User ID     start_date: Start date for analytics     end_date: End date for analytics     period: Predefined period     current_user: Current authenticated user     analytics_service: Analytics service  Returns:     User-specific analytics

### Example

```typescript
import {
    AnalyticsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AnalyticsApi(configuration);

let userId: string; // (default to undefined)
let startDate: string; //Start date for analytics (optional) (default to undefined)
let endDate: string; //End date for analytics (optional) (default to undefined)
let period: string; //Predefined period (1h, 24h, 7d, 30d, 90d) (optional) (default to '7d')

const { status, data } = await apiInstance.getUserAnalyticsApiV1AnalyticsUsersUserIdGet(
    userId,
    startDate,
    endDate,
    period
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userId** | [**string**] |  | defaults to undefined|
| **startDate** | [**string**] | Start date for analytics | (optional) defaults to undefined|
| **endDate** | [**string**] | End date for analytics | (optional) defaults to undefined|
| **period** | [**string**] | Predefined period (1h, 24h, 7d, 30d, 90d) | (optional) defaults to '7d'|


### Return type

**{ [key: string]: any; }**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

