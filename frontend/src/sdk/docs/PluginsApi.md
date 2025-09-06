# PluginsApi

All URIs are relative to *http://localhost:8000*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**bulkDisablePluginsApiV1PluginsBulkDisablePost**](#bulkdisablepluginsapiv1pluginsbulkdisablepost) | **POST** /api/v1/plugins/bulk/disable | Bulk Disable Plugins|
|[**bulkEnablePluginsApiV1PluginsBulkEnablePost**](#bulkenablepluginsapiv1pluginsbulkenablepost) | **POST** /api/v1/plugins/bulk/enable | Bulk Enable Plugins|
|[**checkPluginDependenciesApiV1PluginsPluginIdDependenciesGet**](#checkplugindependenciesapiv1pluginspluginiddependenciesget) | **GET** /api/v1/plugins/{plugin_id}/dependencies | Check Plugin Dependencies|
|[**disablePluginApiV1PluginsPluginIdDisablePost**](#disablepluginapiv1pluginspluginiddisablepost) | **POST** /api/v1/plugins/{plugin_id}/disable | Disable Plugin|
|[**enablePluginApiV1PluginsPluginIdEnablePost**](#enablepluginapiv1pluginspluginidenablepost) | **POST** /api/v1/plugins/{plugin_id}/enable | Enable Plugin|
|[**getPluginApiV1PluginsPluginIdGet**](#getpluginapiv1pluginspluginidget) | **GET** /api/v1/plugins/{plugin_id} | Get Plugin|
|[**getPluginStatsApiV1PluginsStatsGet**](#getpluginstatsapiv1pluginsstatsget) | **GET** /api/v1/plugins/stats | Get Plugin Stats|
|[**healthCheckPluginsApiV1PluginsHealthGet**](#healthcheckpluginsapiv1pluginshealthget) | **GET** /api/v1/plugins/health | Health Check Plugins|
|[**installPluginApiV1PluginsInstallPost**](#installpluginapiv1pluginsinstallpost) | **POST** /api/v1/plugins/install | Install Plugin|
|[**listPluginsApiV1PluginsGet**](#listpluginsapiv1pluginsget) | **GET** /api/v1/plugins/ | List Plugins|
|[**uninstallPluginApiV1PluginsPluginIdDelete**](#uninstallpluginapiv1pluginspluginiddelete) | **DELETE** /api/v1/plugins/{plugin_id} | Uninstall Plugin|
|[**updatePluginApiV1PluginsPluginIdPut**](#updatepluginapiv1pluginspluginidput) | **PUT** /api/v1/plugins/{plugin_id} | Update Plugin|

# **bulkDisablePluginsApiV1PluginsBulkDisablePost**
> { [key: string]: any; } bulkDisablePluginsApiV1PluginsBulkDisablePost(requestBody)

Disable multiple plugins.  Args:     plugin_ids: List of plugin IDs to disable     current_user: Current authenticated user     plugin_manager: Plugin manager instance  Returns:     Bulk operation results

### Example

```typescript
import {
    PluginsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new PluginsApi(configuration);

let requestBody: Array<string>; //

const { status, data } = await apiInstance.bulkDisablePluginsApiV1PluginsBulkDisablePost(
    requestBody
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **Array<string>**|  | |


### Return type

**{ [key: string]: any; }**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **bulkEnablePluginsApiV1PluginsBulkEnablePost**
> { [key: string]: any; } bulkEnablePluginsApiV1PluginsBulkEnablePost(requestBody)

Enable multiple plugins.  Args:     plugin_ids: List of plugin IDs to enable     current_user: Current authenticated user     plugin_manager: Plugin manager instance  Returns:     Bulk operation results

### Example

```typescript
import {
    PluginsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new PluginsApi(configuration);

let requestBody: Array<string | null>; //

const { status, data } = await apiInstance.bulkEnablePluginsApiV1PluginsBulkEnablePost(
    requestBody
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **requestBody** | **Array<string | null>**|  | |


### Return type

**{ [key: string]: any; }**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **checkPluginDependenciesApiV1PluginsPluginIdDependenciesGet**
> { [key: string]: any; } checkPluginDependenciesApiV1PluginsPluginIdDependenciesGet()

Check plugin dependencies.  Args:     plugin_id: Plugin ID     current_user: Current authenticated user     plugin_manager: Plugin manager instance  Returns:     Dependency check results

### Example

```typescript
import {
    PluginsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new PluginsApi(configuration);

let pluginId: string; // (default to undefined)

const { status, data } = await apiInstance.checkPluginDependenciesApiV1PluginsPluginIdDependenciesGet(
    pluginId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pluginId** | [**string**] |  | defaults to undefined|


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

# **disablePluginApiV1PluginsPluginIdDisablePost**
> PluginActionResponse disablePluginApiV1PluginsPluginIdDisablePost()

Disable a plugin.  Args:     plugin_id: Plugin ID     current_user: Current authenticated user     plugin_manager: Plugin manager instance  Returns:     Action result

### Example

```typescript
import {
    PluginsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new PluginsApi(configuration);

let pluginId: string; // (default to undefined)

const { status, data } = await apiInstance.disablePluginApiV1PluginsPluginIdDisablePost(
    pluginId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pluginId** | [**string**] |  | defaults to undefined|


### Return type

**PluginActionResponse**

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

# **enablePluginApiV1PluginsPluginIdEnablePost**
> PluginActionResponse enablePluginApiV1PluginsPluginIdEnablePost()

Enable a plugin.  Args:     plugin_id: Plugin ID     current_user: Current authenticated user     plugin_manager: Plugin manager instance  Returns:     Action result

### Example

```typescript
import {
    PluginsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new PluginsApi(configuration);

let pluginId: string; // (default to undefined)

const { status, data } = await apiInstance.enablePluginApiV1PluginsPluginIdEnablePost(
    pluginId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pluginId** | [**string**] |  | defaults to undefined|


### Return type

**PluginActionResponse**

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

# **getPluginApiV1PluginsPluginIdGet**
> PluginResponse getPluginApiV1PluginsPluginIdGet()

Get plugin by ID.  Args:     plugin_id: Plugin ID     current_user: Current authenticated user     plugin_manager: Plugin manager instance  Returns:     Plugin data

### Example

```typescript
import {
    PluginsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new PluginsApi(configuration);

let pluginId: string; // (default to undefined)

const { status, data } = await apiInstance.getPluginApiV1PluginsPluginIdGet(
    pluginId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pluginId** | [**string**] |  | defaults to undefined|


### Return type

**PluginResponse**

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

# **getPluginStatsApiV1PluginsStatsGet**
> PluginStatsResponse getPluginStatsApiV1PluginsStatsGet()

Get plugin system statistics.  Args:     current_user: Current authenticated user     plugin_manager: Plugin manager instance  Returns:     Plugin system statistics

### Example

```typescript
import {
    PluginsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new PluginsApi(configuration);

const { status, data } = await apiInstance.getPluginStatsApiV1PluginsStatsGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**PluginStatsResponse**

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

# **healthCheckPluginsApiV1PluginsHealthGet**
> PluginHealthCheckResponse healthCheckPluginsApiV1PluginsHealthGet()

Perform health check on all plugins.  Args:     auto_disable_unhealthy: Whether to automatically disable unhealthy plugins     current_user: Current authenticated user     plugin_manager: Plugin manager instance  Returns:     Health check results

### Example

```typescript
import {
    PluginsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new PluginsApi(configuration);

let autoDisableUnhealthy: boolean; // (optional) (default to false)

const { status, data } = await apiInstance.healthCheckPluginsApiV1PluginsHealthGet(
    autoDisableUnhealthy
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **autoDisableUnhealthy** | [**boolean**] |  | (optional) defaults to false|


### Return type

**PluginHealthCheckResponse**

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

# **installPluginApiV1PluginsInstallPost**
> PluginResponse installPluginApiV1PluginsInstallPost(pluginInstallRequest)

Install a new plugin.  Args:     install_data: Plugin installation data     current_user: Current authenticated user     plugin_manager: Plugin manager instance  Returns:     Installed plugin data

### Example

```typescript
import {
    PluginsApi,
    Configuration,
    PluginInstallRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new PluginsApi(configuration);

let pluginInstallRequest: PluginInstallRequest; //

const { status, data } = await apiInstance.installPluginApiV1PluginsInstallPost(
    pluginInstallRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pluginInstallRequest** | **PluginInstallRequest**|  | |


### Return type

**PluginResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listPluginsApiV1PluginsGet**
> PluginListResponse listPluginsApiV1PluginsGet()

List installed plugins with optional filtering.  Args:     request: List request parameters     current_user: Current authenticated user     plugin_manager: Plugin manager instance  Returns:     List of installed plugins

### Example

```typescript
import {
    PluginsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new PluginsApi(configuration);

let pluginType: PluginType; // (optional) (default to undefined)
let status: PluginStatus; // (optional) (default to undefined)
let enabled: boolean; // (optional) (default to undefined)

const { status, data } = await apiInstance.listPluginsApiV1PluginsGet(
    pluginType,
    status,
    enabled
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pluginType** | **PluginType** |  | (optional) defaults to undefined|
| **status** | **PluginStatus** |  | (optional) defaults to undefined|
| **enabled** | [**boolean**] |  | (optional) defaults to undefined|


### Return type

**PluginListResponse**

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

# **uninstallPluginApiV1PluginsPluginIdDelete**
> PluginDeleteResponse uninstallPluginApiV1PluginsPluginIdDelete()

Uninstall a plugin.  Args:     plugin_id: Plugin ID     current_user: Current authenticated user     plugin_manager: Plugin manager instance  Returns:     Uninstall result

### Example

```typescript
import {
    PluginsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new PluginsApi(configuration);

let pluginId: string; // (default to undefined)

const { status, data } = await apiInstance.uninstallPluginApiV1PluginsPluginIdDelete(
    pluginId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pluginId** | [**string**] |  | defaults to undefined|


### Return type

**PluginDeleteResponse**

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

# **updatePluginApiV1PluginsPluginIdPut**
> PluginResponse updatePluginApiV1PluginsPluginIdPut(pluginUpdateRequest)

Update a plugin.  Args:     plugin_id: Plugin ID     update_data: Plugin update data     current_user: Current authenticated user     plugin_manager: Plugin manager instance  Returns:     Updated plugin data

### Example

```typescript
import {
    PluginsApi,
    Configuration,
    PluginUpdateRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new PluginsApi(configuration);

let pluginId: string; // (default to undefined)
let pluginUpdateRequest: PluginUpdateRequest; //

const { status, data } = await apiInstance.updatePluginApiV1PluginsPluginIdPut(
    pluginId,
    pluginUpdateRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **pluginUpdateRequest** | **PluginUpdateRequest**|  | |
| **pluginId** | [**string**] |  | defaults to undefined|


### Return type

**PluginResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

