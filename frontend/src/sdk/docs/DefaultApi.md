# DefaultApi

All URIs are relative to *http://localhost:8000*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**rootGet**](#rootget) | **GET** / | Root|
|[**serveReactAppFullPathGet**](#servereactappfullpathget) | **GET** /{full_path} | Serve React App|

# **rootGet**
> any rootGet()

Root endpoint.

### Example

```typescript
import {
    DefaultApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

const { status, data } = await apiInstance.rootGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**any**

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

# **serveReactAppFullPathGet**
> any serveReactAppFullPathGet()


### Example

```typescript
import {
    DefaultApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new DefaultApi(configuration);

let fullPath: string; // (default to undefined)

const { status, data } = await apiInstance.serveReactAppFullPathGet(
    fullPath
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **fullPath** | [**string**] |  | defaults to undefined|


### Return type

**any**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

