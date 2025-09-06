# EventsApi

All URIs are relative to *http://localhost:8000*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**adminEventsStreamApiV1EventsAdminStreamGet**](#admineventsstreamapiv1eventsadminstreamget) | **GET** /api/v1/events/admin/stream | Admin Events Stream|
|[**eventsStreamApiV1EventsStreamGet**](#eventsstreamapiv1eventsstreamget) | **GET** /api/v1/events/stream | Events Stream|
|[**getSseStatsApiV1EventsStatsGet**](#getssestatsapiv1eventsstatsget) | **GET** /api/v1/events/stats | Get Sse Stats|
|[**triggerBroadcastTestApiV1EventsBroadcastTestPost**](#triggerbroadcasttestapiv1eventsbroadcasttestpost) | **POST** /api/v1/events/broadcast-test | Trigger Broadcast Test|
|[**triggerTestEventApiV1EventsTestEventPost**](#triggertesteventapiv1eventstesteventpost) | **POST** /api/v1/events/test-event | Trigger Test Event|

# **adminEventsStreamApiV1EventsAdminStreamGet**
> any adminEventsStreamApiV1EventsAdminStreamGet()

Stream all system events for admin users.  Args:     request: FastAPI request object     current_user: Current authenticated admin user  Returns:     StreamingResponse with SSE format for all events

### Example

```typescript
import {
    EventsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new EventsApi(configuration);

const { status, data } = await apiInstance.adminEventsStreamApiV1EventsAdminStreamGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**any**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, text/event-stream


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Admin SSE stream for all system events |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **eventsStreamApiV1EventsStreamGet**
> any eventsStreamApiV1EventsStreamGet()

Stream real-time events via Server-Sent Events.  Args:     request: FastAPI request object     current_user: Current authenticated user  Returns:     StreamingResponse with SSE format

### Example

```typescript
import {
    EventsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new EventsApi(configuration);

const { status, data } = await apiInstance.eventsStreamApiV1EventsStreamGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**any**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, text/event-stream


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Server-Sent Events stream for real-time updates |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getSseStatsApiV1EventsStatsGet**
> SSEStatsResponse getSseStatsApiV1EventsStatsGet()

Get SSE service statistics.  Args:     current_user: Current authenticated admin user  Returns:     SSE service statistics

### Example

```typescript
import {
    EventsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new EventsApi(configuration);

const { status, data } = await apiInstance.getSseStatsApiV1EventsStatsGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**SSEStatsResponse**

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

# **triggerBroadcastTestApiV1EventsBroadcastTestPost**
> TestEventResponse triggerBroadcastTestApiV1EventsBroadcastTestPost()

Trigger a broadcast test event for all users.  Args:     current_user: Current authenticated admin user  Returns:     Success message with event ID

### Example

```typescript
import {
    EventsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new EventsApi(configuration);

const { status, data } = await apiInstance.triggerBroadcastTestApiV1EventsBroadcastTestPost();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**TestEventResponse**

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

# **triggerTestEventApiV1EventsTestEventPost**
> TestEventResponse triggerTestEventApiV1EventsTestEventPost()

Trigger a test event for the current user.  Args:     current_user: Current authenticated user  Returns:     Success message with event ID

### Example

```typescript
import {
    EventsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new EventsApi(configuration);

const { status, data } = await apiInstance.triggerTestEventApiV1EventsTestEventPost();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**TestEventResponse**

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

