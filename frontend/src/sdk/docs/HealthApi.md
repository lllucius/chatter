# HealthApi

All URIs are relative to *http://localhost:8000*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**healthCheckEndpointHealthzGet**](#healthcheckendpointhealthzget) | **GET** /healthz | Health Check Endpoint|
|[**livenessCheckLiveGet**](#livenesscheckliveget) | **GET** /live | Liveness Check|
|[**readinessCheckReadyzGet**](#readinesscheckreadyzget) | **GET** /readyz | Readiness Check|

# **healthCheckEndpointHealthzGet**
> HealthCheckResponse healthCheckEndpointHealthzGet()

Basic health check endpoint.  Returns:     Health status

### Example

```typescript
import {
    HealthApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.healthCheckEndpointHealthzGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**HealthCheckResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **livenessCheckLiveGet**
> HealthCheckResponse livenessCheckLiveGet()

Liveness check endpoint for Kubernetes (alias for /healthz).  Returns:     Health status (same as /healthz)

### Example

```typescript
import {
    HealthApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.livenessCheckLiveGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**HealthCheckResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **readinessCheckReadyzGet**
> ReadinessCheckResponse readinessCheckReadyzGet()

Readiness check endpoint with database connectivity.  Args:     session: Database session  Returns:     Readiness status with detailed checks

### Example

```typescript
import {
    HealthApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new HealthApi(configuration);

const { status, data } = await apiInstance.readinessCheckReadyzGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**ReadinessCheckResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

