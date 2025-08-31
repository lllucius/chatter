# ToolServersApi

All URIs are relative to *http://localhost:8000*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**bulkServerOperationApiV1ToolserversServersBulkPost**](#bulkserveroperationapiv1toolserversserversbulkpost) | **POST** /api/v1/toolservers/servers/bulk | Bulk Server Operation|
|[**checkServerHealthApiV1ToolserversServersServerIdHealthGet**](#checkserverhealthapiv1toolserversserversserveridhealthget) | **GET** /api/v1/toolservers/servers/{server_id}/health | Check Server Health|
|[**checkToolAccessApiV1ToolserversAccessCheckPost**](#checktoolaccessapiv1toolserversaccesscheckpost) | **POST** /api/v1/toolservers/access-check | Check Tool Access|
|[**createRoleAccessRuleApiV1ToolserversRoleAccessPost**](#createroleaccessruleapiv1toolserversroleaccesspost) | **POST** /api/v1/toolservers/role-access | Create Role Access Rule|
|[**createToolServerApiV1ToolserversServersPost**](#createtoolserverapiv1toolserversserverspost) | **POST** /api/v1/toolservers/servers | Create Tool Server|
|[**deleteToolServerApiV1ToolserversServersServerIdDelete**](#deletetoolserverapiv1toolserversserversserveriddelete) | **DELETE** /api/v1/toolservers/servers/{server_id} | Delete Tool Server|
|[**disableToolApiV1ToolserversToolsToolIdDisablePost**](#disabletoolapiv1toolserverstoolstooliddisablepost) | **POST** /api/v1/toolservers/tools/{tool_id}/disable | Disable Tool|
|[**disableToolServerApiV1ToolserversServersServerIdDisablePost**](#disabletoolserverapiv1toolserversserversserveriddisablepost) | **POST** /api/v1/toolservers/servers/{server_id}/disable | Disable Tool Server|
|[**enableToolApiV1ToolserversToolsToolIdEnablePost**](#enabletoolapiv1toolserverstoolstoolidenablepost) | **POST** /api/v1/toolservers/tools/{tool_id}/enable | Enable Tool|
|[**enableToolServerApiV1ToolserversServersServerIdEnablePost**](#enabletoolserverapiv1toolserversserversserveridenablepost) | **POST** /api/v1/toolservers/servers/{server_id}/enable | Enable Tool Server|
|[**getRoleAccessRulesApiV1ToolserversRoleAccessGet**](#getroleaccessrulesapiv1toolserversroleaccessget) | **GET** /api/v1/toolservers/role-access | Get Role Access Rules|
|[**getServerMetricsApiV1ToolserversServersServerIdMetricsGet**](#getservermetricsapiv1toolserversserversserveridmetricsget) | **GET** /api/v1/toolservers/servers/{server_id}/metrics | Get Server Metrics|
|[**getServerToolsApiV1ToolserversServersServerIdToolsGet**](#getservertoolsapiv1toolserversserversserveridtoolsget) | **GET** /api/v1/toolservers/servers/{server_id}/tools | Get Server Tools|
|[**getToolServerApiV1ToolserversServersServerIdGet**](#gettoolserverapiv1toolserversserversserveridget) | **GET** /api/v1/toolservers/servers/{server_id} | Get Tool Server|
|[**getUserPermissionsApiV1ToolserversUsersUserIdPermissionsGet**](#getuserpermissionsapiv1toolserversusersuseridpermissionsget) | **GET** /api/v1/toolservers/users/{user_id}/permissions | Get User Permissions|
|[**grantToolPermissionApiV1ToolserversPermissionsPost**](#granttoolpermissionapiv1toolserverspermissionspost) | **POST** /api/v1/toolservers/permissions | Grant Tool Permission|
|[**listAllToolsApiV1ToolserversToolsAllGet**](#listalltoolsapiv1toolserverstoolsallget) | **GET** /api/v1/toolservers/tools/all | List All Tools|
|[**listToolServersApiV1ToolserversServersGet**](#listtoolserversapiv1toolserversserversget) | **GET** /api/v1/toolservers/servers | List Tool Servers|
|[**refreshServerToolsApiV1ToolserversServersServerIdRefreshToolsPost**](#refreshservertoolsapiv1toolserversserversserveridrefreshtoolspost) | **POST** /api/v1/toolservers/servers/{server_id}/refresh-tools | Refresh Server Tools|
|[**restartToolServerApiV1ToolserversServersServerIdRestartPost**](#restarttoolserverapiv1toolserversserversserveridrestartpost) | **POST** /api/v1/toolservers/servers/{server_id}/restart | Restart Tool Server|
|[**revokeToolPermissionApiV1ToolserversPermissionsPermissionIdDelete**](#revoketoolpermissionapiv1toolserverspermissionspermissioniddelete) | **DELETE** /api/v1/toolservers/permissions/{permission_id} | Revoke Tool Permission|
|[**startToolServerApiV1ToolserversServersServerIdStartPost**](#starttoolserverapiv1toolserversserversserveridstartpost) | **POST** /api/v1/toolservers/servers/{server_id}/start | Start Tool Server|
|[**stopToolServerApiV1ToolserversServersServerIdStopPost**](#stoptoolserverapiv1toolserversserversserveridstoppost) | **POST** /api/v1/toolservers/servers/{server_id}/stop | Stop Tool Server|
|[**testServerConnectivityApiV1ToolserversServersServerIdTestConnectivityPost**](#testserverconnectivityapiv1toolserversserversserveridtestconnectivitypost) | **POST** /api/v1/toolservers/servers/{server_id}/test-connectivity | Test Server Connectivity|
|[**updateToolPermissionApiV1ToolserversPermissionsPermissionIdPut**](#updatetoolpermissionapiv1toolserverspermissionspermissionidput) | **PUT** /api/v1/toolservers/permissions/{permission_id} | Update Tool Permission|
|[**updateToolServerApiV1ToolserversServersServerIdPut**](#updatetoolserverapiv1toolserversserversserveridput) | **PUT** /api/v1/toolservers/servers/{server_id} | Update Tool Server|

# **bulkServerOperationApiV1ToolserversServersBulkPost**
> BulkOperationResult bulkServerOperationApiV1ToolserversServersBulkPost(bulkToolServerOperation)

Perform bulk operations on multiple servers.  Args:     operation_data: Bulk operation data     current_user: Current authenticated user     service: Tool server service  Returns:     Bulk operation result

### Example

```typescript
import {
    ToolServersApi,
    Configuration,
    BulkToolServerOperation
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let bulkToolServerOperation: BulkToolServerOperation; //

const { status, data } = await apiInstance.bulkServerOperationApiV1ToolserversServersBulkPost(
    bulkToolServerOperation
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **bulkToolServerOperation** | **BulkToolServerOperation**|  | |


### Return type

**BulkOperationResult**

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

# **checkServerHealthApiV1ToolserversServersServerIdHealthGet**
> ToolServerHealthCheck checkServerHealthApiV1ToolserversServersServerIdHealthGet()

Perform health check on a server.  Args:     server_id: Server ID     current_user: Current authenticated user     service: Tool server service  Returns:     Health check result

### Example

```typescript
import {
    ToolServersApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let serverId: string; // (default to undefined)

const { status, data } = await apiInstance.checkServerHealthApiV1ToolserversServersServerIdHealthGet(
    serverId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **serverId** | [**string**] |  | defaults to undefined|


### Return type

**ToolServerHealthCheck**

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

# **checkToolAccessApiV1ToolserversAccessCheckPost**
> ToolAccessResult checkToolAccessApiV1ToolserversAccessCheckPost(userToolAccessCheck)

Check if user has access to a tool.  Args:     check_data: Access check data     current_user: Current authenticated user     access_service: Tool access service  Returns:     Access check result

### Example

```typescript
import {
    ToolServersApi,
    Configuration,
    UserToolAccessCheck
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let userToolAccessCheck: UserToolAccessCheck; //

const { status, data } = await apiInstance.checkToolAccessApiV1ToolserversAccessCheckPost(
    userToolAccessCheck
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userToolAccessCheck** | **UserToolAccessCheck**|  | |


### Return type

**ToolAccessResult**

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

# **createRoleAccessRuleApiV1ToolserversRoleAccessPost**
> RoleToolAccessResponse createRoleAccessRuleApiV1ToolserversRoleAccessPost(roleToolAccessCreate)

Create role-based access rule.  Args:     rule_data: Rule data     current_user: Current authenticated user     access_service: Tool access service  Returns:     Created rule

### Example

```typescript
import {
    ToolServersApi,
    Configuration,
    RoleToolAccessCreate
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let roleToolAccessCreate: RoleToolAccessCreate; //

const { status, data } = await apiInstance.createRoleAccessRuleApiV1ToolserversRoleAccessPost(
    roleToolAccessCreate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **roleToolAccessCreate** | **RoleToolAccessCreate**|  | |


### Return type

**RoleToolAccessResponse**

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

# **createToolServerApiV1ToolserversServersPost**
> ToolServerResponse createToolServerApiV1ToolserversServersPost(toolServerCreate)

Create a new tool server.  Args:     server_data: Server creation data     current_user: Current authenticated user     service: Tool server service  Returns:     Created server response

### Example

```typescript
import {
    ToolServersApi,
    Configuration,
    ToolServerCreate
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let toolServerCreate: ToolServerCreate; //

const { status, data } = await apiInstance.createToolServerApiV1ToolserversServersPost(
    toolServerCreate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **toolServerCreate** | **ToolServerCreate**|  | |


### Return type

**ToolServerResponse**

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

# **deleteToolServerApiV1ToolserversServersServerIdDelete**
> ToolServerDeleteResponse deleteToolServerApiV1ToolserversServersServerIdDelete()

Delete a tool server.  Args:     server_id: Server ID     current_user: Current authenticated user     service: Tool server service  Returns:     Success message

### Example

```typescript
import {
    ToolServersApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let serverId: string; // (default to undefined)

const { status, data } = await apiInstance.deleteToolServerApiV1ToolserversServersServerIdDelete(
    serverId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **serverId** | [**string**] |  | defaults to undefined|


### Return type

**ToolServerDeleteResponse**

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

# **disableToolApiV1ToolserversToolsToolIdDisablePost**
> ToolOperationResponse disableToolApiV1ToolserversToolsToolIdDisablePost()

Disable a specific tool.  Args:     tool_id: Tool ID     current_user: Current authenticated user     service: Tool server service  Returns:     Operation result

### Example

```typescript
import {
    ToolServersApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let toolId: string; // (default to undefined)

const { status, data } = await apiInstance.disableToolApiV1ToolserversToolsToolIdDisablePost(
    toolId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **toolId** | [**string**] |  | defaults to undefined|


### Return type

**ToolOperationResponse**

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

# **disableToolServerApiV1ToolserversServersServerIdDisablePost**
> ToolServerOperationResponse disableToolServerApiV1ToolserversServersServerIdDisablePost()

Disable a tool server.  Args:     server_id: Server ID     current_user: Current authenticated user     service: Tool server service  Returns:     Operation result

### Example

```typescript
import {
    ToolServersApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let serverId: string; // (default to undefined)

const { status, data } = await apiInstance.disableToolServerApiV1ToolserversServersServerIdDisablePost(
    serverId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **serverId** | [**string**] |  | defaults to undefined|


### Return type

**ToolServerOperationResponse**

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

# **enableToolApiV1ToolserversToolsToolIdEnablePost**
> ToolOperationResponse enableToolApiV1ToolserversToolsToolIdEnablePost()

Enable a specific tool.  Args:     tool_id: Tool ID     current_user: Current authenticated user     service: Tool server service  Returns:     Operation result

### Example

```typescript
import {
    ToolServersApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let toolId: string; // (default to undefined)

const { status, data } = await apiInstance.enableToolApiV1ToolserversToolsToolIdEnablePost(
    toolId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **toolId** | [**string**] |  | defaults to undefined|


### Return type

**ToolOperationResponse**

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

# **enableToolServerApiV1ToolserversServersServerIdEnablePost**
> ToolServerOperationResponse enableToolServerApiV1ToolserversServersServerIdEnablePost()

Enable a tool server.  Args:     server_id: Server ID     current_user: Current authenticated user     service: Tool server service  Returns:     Operation result

### Example

```typescript
import {
    ToolServersApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let serverId: string; // (default to undefined)

const { status, data } = await apiInstance.enableToolServerApiV1ToolserversServersServerIdEnablePost(
    serverId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **serverId** | [**string**] |  | defaults to undefined|


### Return type

**ToolServerOperationResponse**

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

# **getRoleAccessRulesApiV1ToolserversRoleAccessGet**
> Array<RoleToolAccessResponse> getRoleAccessRulesApiV1ToolserversRoleAccessGet()

Get role-based access rules.  Args:     role: Optional role filter     current_user: Current authenticated user     access_service: Tool access service  Returns:     List of access rules

### Example

```typescript
import {
    ToolServersApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let role: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.getRoleAccessRulesApiV1ToolserversRoleAccessGet(
    role
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **role** | [**string**] |  | (optional) defaults to undefined|


### Return type

**Array<RoleToolAccessResponse>**

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

# **getServerMetricsApiV1ToolserversServersServerIdMetricsGet**
> ToolServerMetrics getServerMetricsApiV1ToolserversServersServerIdMetricsGet()

Get analytics for a specific server.  Args:     server_id: Server ID     current_user: Current authenticated user     service: Tool server service  Returns:     Server metrics

### Example

```typescript
import {
    ToolServersApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let serverId: string; // (default to undefined)

const { status, data } = await apiInstance.getServerMetricsApiV1ToolserversServersServerIdMetricsGet(
    serverId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **serverId** | [**string**] |  | defaults to undefined|


### Return type

**ToolServerMetrics**

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

# **getServerToolsApiV1ToolserversServersServerIdToolsGet**
> ServerToolsResponse getServerToolsApiV1ToolserversServersServerIdToolsGet()

Get tools for a specific server.  Args:     server_id: Server ID     request: Server tools request with pagination     current_user: Current authenticated user     service: Tool server service  Returns:     List of server tools with pagination

### Example

```typescript
import {
    ToolServersApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let serverId: string; // (default to undefined)
let limit: number; // (optional) (default to 50)
let offset: number; // (optional) (default to 0)

const { status, data } = await apiInstance.getServerToolsApiV1ToolserversServersServerIdToolsGet(
    serverId,
    limit,
    offset
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **serverId** | [**string**] |  | defaults to undefined|
| **limit** | [**number**] |  | (optional) defaults to 50|
| **offset** | [**number**] |  | (optional) defaults to 0|


### Return type

**ServerToolsResponse**

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

# **getToolServerApiV1ToolserversServersServerIdGet**
> ToolServerResponse getToolServerApiV1ToolserversServersServerIdGet()

Get a tool server by ID.  Args:     server_id: Server ID     current_user: Current authenticated user     service: Tool server service  Returns:     Server response

### Example

```typescript
import {
    ToolServersApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let serverId: string; // (default to undefined)

const { status, data } = await apiInstance.getToolServerApiV1ToolserversServersServerIdGet(
    serverId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **serverId** | [**string**] |  | defaults to undefined|


### Return type

**ToolServerResponse**

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

# **getUserPermissionsApiV1ToolserversUsersUserIdPermissionsGet**
> Array<ToolPermissionResponse> getUserPermissionsApiV1ToolserversUsersUserIdPermissionsGet()

Get all permissions for a user.  Args:     user_id: User ID     current_user: Current authenticated user     access_service: Tool access service  Returns:     List of user permissions

### Example

```typescript
import {
    ToolServersApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let userId: string; // (default to undefined)

const { status, data } = await apiInstance.getUserPermissionsApiV1ToolserversUsersUserIdPermissionsGet(
    userId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userId** | [**string**] |  | defaults to undefined|


### Return type

**Array<ToolPermissionResponse>**

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

# **grantToolPermissionApiV1ToolserversPermissionsPost**
> ToolPermissionResponse grantToolPermissionApiV1ToolserversPermissionsPost(toolPermissionCreate)

Grant tool permission to a user.  Args:     permission_data: Permission data     current_user: Current authenticated user     access_service: Tool access service  Returns:     Created permission

### Example

```typescript
import {
    ToolServersApi,
    Configuration,
    ToolPermissionCreate
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let toolPermissionCreate: ToolPermissionCreate; //

const { status, data } = await apiInstance.grantToolPermissionApiV1ToolserversPermissionsPost(
    toolPermissionCreate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **toolPermissionCreate** | **ToolPermissionCreate**|  | |


### Return type

**ToolPermissionResponse**

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

# **listAllToolsApiV1ToolserversToolsAllGet**
> Array<{ [key: string]: any; }> listAllToolsApiV1ToolserversToolsAllGet()

List all tools across all servers.  Args:     current_user: Current authenticated user     tool_server_service: Tool server service  Returns:     List of all available tools across all servers

### Example

```typescript
import {
    ToolServersApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

const { status, data } = await apiInstance.listAllToolsApiV1ToolserversToolsAllGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**Array<{ [key: string]: any; }>**

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

# **listToolServersApiV1ToolserversServersGet**
> Array<ToolServerResponse> listToolServersApiV1ToolserversServersGet()

List tool servers with optional filtering.  Args:     request: List request with filter parameters     current_user: Current authenticated user     service: Tool server service  Returns:     List of server responses

### Example

```typescript
import {
    ToolServersApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let status: ServerStatus; // (optional) (default to undefined)
let includeBuiltin: boolean; // (optional) (default to true)

const { status, data } = await apiInstance.listToolServersApiV1ToolserversServersGet(
    status,
    includeBuiltin
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **status** | **ServerStatus** |  | (optional) defaults to undefined|
| **includeBuiltin** | [**boolean**] |  | (optional) defaults to true|


### Return type

**Array<ToolServerResponse>**

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

# **refreshServerToolsApiV1ToolserversServersServerIdRefreshToolsPost**
> { [key: string]: any; } refreshServerToolsApiV1ToolserversServersServerIdRefreshToolsPost()

Refresh tools for a remote server.  Args:     server_id: Server ID     current_user: Current authenticated user     service: Tool server service  Returns:     Refresh result

### Example

```typescript
import {
    ToolServersApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let serverId: string; // (default to undefined)

const { status, data } = await apiInstance.refreshServerToolsApiV1ToolserversServersServerIdRefreshToolsPost(
    serverId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **serverId** | [**string**] |  | defaults to undefined|


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

# **restartToolServerApiV1ToolserversServersServerIdRestartPost**
> ToolServerOperationResponse restartToolServerApiV1ToolserversServersServerIdRestartPost()

Restart a tool server.  Args:     server_id: Server ID     current_user: Current authenticated user     service: Tool server service  Returns:     Operation result

### Example

```typescript
import {
    ToolServersApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let serverId: string; // (default to undefined)

const { status, data } = await apiInstance.restartToolServerApiV1ToolserversServersServerIdRestartPost(
    serverId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **serverId** | [**string**] |  | defaults to undefined|


### Return type

**ToolServerOperationResponse**

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

# **revokeToolPermissionApiV1ToolserversPermissionsPermissionIdDelete**
> { [key: string]: any; } revokeToolPermissionApiV1ToolserversPermissionsPermissionIdDelete()

Revoke tool permission.  Args:     permission_id: Permission ID     current_user: Current authenticated user     access_service: Tool access service  Returns:     Success message

### Example

```typescript
import {
    ToolServersApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let permissionId: string; // (default to undefined)

const { status, data } = await apiInstance.revokeToolPermissionApiV1ToolserversPermissionsPermissionIdDelete(
    permissionId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **permissionId** | [**string**] |  | defaults to undefined|


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

# **startToolServerApiV1ToolserversServersServerIdStartPost**
> ToolServerOperationResponse startToolServerApiV1ToolserversServersServerIdStartPost()

Start a tool server.  Args:     server_id: Server ID     current_user: Current authenticated user     service: Tool server service  Returns:     Operation result

### Example

```typescript
import {
    ToolServersApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let serverId: string; // (default to undefined)

const { status, data } = await apiInstance.startToolServerApiV1ToolserversServersServerIdStartPost(
    serverId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **serverId** | [**string**] |  | defaults to undefined|


### Return type

**ToolServerOperationResponse**

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

# **stopToolServerApiV1ToolserversServersServerIdStopPost**
> ToolServerOperationResponse stopToolServerApiV1ToolserversServersServerIdStopPost()

Stop a tool server.  Args:     server_id: Server ID     current_user: Current authenticated user     service: Tool server service  Returns:     Operation result

### Example

```typescript
import {
    ToolServersApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let serverId: string; // (default to undefined)

const { status, data } = await apiInstance.stopToolServerApiV1ToolserversServersServerIdStopPost(
    serverId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **serverId** | [**string**] |  | defaults to undefined|


### Return type

**ToolServerOperationResponse**

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

# **testServerConnectivityApiV1ToolserversServersServerIdTestConnectivityPost**
> { [key: string]: any; } testServerConnectivityApiV1ToolserversServersServerIdTestConnectivityPost()

Test connectivity to an external MCP server.  Args:     server_id: Tool server ID     current_user: Current authenticated user     tool_server_service: Tool server service  Returns:     Connectivity test results

### Example

```typescript
import {
    ToolServersApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let serverId: string; // (default to undefined)

const { status, data } = await apiInstance.testServerConnectivityApiV1ToolserversServersServerIdTestConnectivityPost(
    serverId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **serverId** | [**string**] |  | defaults to undefined|


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

# **updateToolPermissionApiV1ToolserversPermissionsPermissionIdPut**
> ToolPermissionResponse updateToolPermissionApiV1ToolserversPermissionsPermissionIdPut(toolPermissionUpdate)

Update tool permission.  Args:     permission_id: Permission ID     update_data: Update data     current_user: Current authenticated user     access_service: Tool access service  Returns:     Updated permission

### Example

```typescript
import {
    ToolServersApi,
    Configuration,
    ToolPermissionUpdate
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let permissionId: string; // (default to undefined)
let toolPermissionUpdate: ToolPermissionUpdate; //

const { status, data } = await apiInstance.updateToolPermissionApiV1ToolserversPermissionsPermissionIdPut(
    permissionId,
    toolPermissionUpdate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **toolPermissionUpdate** | **ToolPermissionUpdate**|  | |
| **permissionId** | [**string**] |  | defaults to undefined|


### Return type

**ToolPermissionResponse**

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

# **updateToolServerApiV1ToolserversServersServerIdPut**
> ToolServerResponse updateToolServerApiV1ToolserversServersServerIdPut(toolServerUpdate)

Update a tool server.  Args:     server_id: Server ID     update_data: Update data     current_user: Current authenticated user     service: Tool server service  Returns:     Updated server response

### Example

```typescript
import {
    ToolServersApi,
    Configuration,
    ToolServerUpdate
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ToolServersApi(configuration);

let serverId: string; // (default to undefined)
let toolServerUpdate: ToolServerUpdate; //

const { status, data } = await apiInstance.updateToolServerApiV1ToolserversServersServerIdPut(
    serverId,
    toolServerUpdate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **toolServerUpdate** | **ToolServerUpdate**|  | |
| **serverId** | [**string**] |  | defaults to undefined|


### Return type

**ToolServerResponse**

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

