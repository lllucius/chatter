# AgentsApi

All URIs are relative to *http://localhost:8000*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**bulkCreateAgentsApiV1AgentsBulkPost**](#bulkcreateagentsapiv1agentsbulkpost) | **POST** /api/v1/agents/bulk | Bulk Create Agents|
|[**bulkCreateAgentsApiV1AgentsBulkPost_0**](#bulkcreateagentsapiv1agentsbulkpost_0) | **POST** /api/v1/agents/bulk | Bulk Create Agents|
|[**bulkDeleteAgentsApiV1AgentsBulkDelete**](#bulkdeleteagentsapiv1agentsbulkdelete) | **DELETE** /api/v1/agents/bulk | Bulk Delete Agents|
|[**bulkDeleteAgentsApiV1AgentsBulkDelete_0**](#bulkdeleteagentsapiv1agentsbulkdelete_0) | **DELETE** /api/v1/agents/bulk | Bulk Delete Agents|
|[**createAgentApiV1AgentsPost**](#createagentapiv1agentspost) | **POST** /api/v1/agents/ | Create a new agent|
|[**createAgentApiV1AgentsPost_0**](#createagentapiv1agentspost_0) | **POST** /api/v1/agents/ | Create a new agent|
|[**deleteAgentApiV1AgentsAgentIdDelete**](#deleteagentapiv1agentsagentiddelete) | **DELETE** /api/v1/agents/{agent_id} | Delete Agent|
|[**deleteAgentApiV1AgentsAgentIdDelete_0**](#deleteagentapiv1agentsagentiddelete_0) | **DELETE** /api/v1/agents/{agent_id} | Delete Agent|
|[**getAgentApiV1AgentsAgentIdGet**](#getagentapiv1agentsagentidget) | **GET** /api/v1/agents/{agent_id} | Get Agent|
|[**getAgentApiV1AgentsAgentIdGet_0**](#getagentapiv1agentsagentidget_0) | **GET** /api/v1/agents/{agent_id} | Get Agent|
|[**getAgentHealthApiV1AgentsAgentIdHealthGet**](#getagenthealthapiv1agentsagentidhealthget) | **GET** /api/v1/agents/{agent_id}/health | Get Agent Health|
|[**getAgentHealthApiV1AgentsAgentIdHealthGet_0**](#getagenthealthapiv1agentsagentidhealthget_0) | **GET** /api/v1/agents/{agent_id}/health | Get Agent Health|
|[**getAgentStatsApiV1AgentsStatsOverviewGet**](#getagentstatsapiv1agentsstatsoverviewget) | **GET** /api/v1/agents/stats/overview | Get agent statistics|
|[**getAgentStatsApiV1AgentsStatsOverviewGet_0**](#getagentstatsapiv1agentsstatsoverviewget_0) | **GET** /api/v1/agents/stats/overview | Get agent statistics|
|[**getAgentTemplatesApiV1AgentsTemplatesGet**](#getagenttemplatesapiv1agentstemplatesget) | **GET** /api/v1/agents/templates | Get agent templates|
|[**getAgentTemplatesApiV1AgentsTemplatesGet_0**](#getagenttemplatesapiv1agentstemplatesget_0) | **GET** /api/v1/agents/templates | Get agent templates|
|[**interactWithAgentApiV1AgentsAgentIdInteractPost**](#interactwithagentapiv1agentsagentidinteractpost) | **POST** /api/v1/agents/{agent_id}/interact | Interact with agent|
|[**interactWithAgentApiV1AgentsAgentIdInteractPost_0**](#interactwithagentapiv1agentsagentidinteractpost_0) | **POST** /api/v1/agents/{agent_id}/interact | Interact with agent|
|[**listAgentsApiV1AgentsGet**](#listagentsapiv1agentsget) | **GET** /api/v1/agents/ | List agents|
|[**listAgentsApiV1AgentsGet_0**](#listagentsapiv1agentsget_0) | **GET** /api/v1/agents/ | List agents|
|[**updateAgentApiV1AgentsAgentIdPut**](#updateagentapiv1agentsagentidput) | **PUT** /api/v1/agents/{agent_id} | Update Agent|
|[**updateAgentApiV1AgentsAgentIdPut_0**](#updateagentapiv1agentsagentidput_0) | **PUT** /api/v1/agents/{agent_id} | Update Agent|

# **bulkCreateAgentsApiV1AgentsBulkPost**
> AgentBulkCreateResponse bulkCreateAgentsApiV1AgentsBulkPost(agentBulkCreateRequest)

Create multiple agents in bulk.  Args:     request: Bulk creation request     current_user: Current authenticated user     agent_manager: Agent manager instance  Returns:     Bulk creation results

### Example

```typescript
import {
    AgentsApi,
    Configuration,
    AgentBulkCreateRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let agentBulkCreateRequest: AgentBulkCreateRequest; //

const { status, data } = await apiInstance.bulkCreateAgentsApiV1AgentsBulkPost(
    agentBulkCreateRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **agentBulkCreateRequest** | **AgentBulkCreateRequest**|  | |


### Return type

**AgentBulkCreateResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**400** | Bad request |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**404** | Not found |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **bulkCreateAgentsApiV1AgentsBulkPost_0**
> AgentBulkCreateResponse bulkCreateAgentsApiV1AgentsBulkPost_0(agentBulkCreateRequest)

Create multiple agents in bulk.  Args:     request: Bulk creation request     current_user: Current authenticated user     agent_manager: Agent manager instance  Returns:     Bulk creation results

### Example

```typescript
import {
    AgentsApi,
    Configuration,
    AgentBulkCreateRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let agentBulkCreateRequest: AgentBulkCreateRequest; //

const { status, data } = await apiInstance.bulkCreateAgentsApiV1AgentsBulkPost_0(
    agentBulkCreateRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **agentBulkCreateRequest** | **AgentBulkCreateRequest**|  | |


### Return type

**AgentBulkCreateResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**400** | Bad request |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**404** | Not found |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **bulkDeleteAgentsApiV1AgentsBulkDelete**
> { [key: string]: any; } bulkDeleteAgentsApiV1AgentsBulkDelete(agentBulkDeleteRequest)

Delete multiple agents in bulk.  Args:     request: Bulk deletion request     current_user: Current authenticated user     agent_manager: Agent manager instance  Returns:     Bulk deletion results

### Example

```typescript
import {
    AgentsApi,
    Configuration,
    AgentBulkDeleteRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let agentBulkDeleteRequest: AgentBulkDeleteRequest; //

const { status, data } = await apiInstance.bulkDeleteAgentsApiV1AgentsBulkDelete(
    agentBulkDeleteRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **agentBulkDeleteRequest** | **AgentBulkDeleteRequest**|  | |


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
|**400** | Bad request |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**404** | Not found |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **bulkDeleteAgentsApiV1AgentsBulkDelete_0**
> { [key: string]: any; } bulkDeleteAgentsApiV1AgentsBulkDelete_0(agentBulkDeleteRequest)

Delete multiple agents in bulk.  Args:     request: Bulk deletion request     current_user: Current authenticated user     agent_manager: Agent manager instance  Returns:     Bulk deletion results

### Example

```typescript
import {
    AgentsApi,
    Configuration,
    AgentBulkDeleteRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let agentBulkDeleteRequest: AgentBulkDeleteRequest; //

const { status, data } = await apiInstance.bulkDeleteAgentsApiV1AgentsBulkDelete_0(
    agentBulkDeleteRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **agentBulkDeleteRequest** | **AgentBulkDeleteRequest**|  | |


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
|**400** | Bad request |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**404** | Not found |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createAgentApiV1AgentsPost**
> AgentResponse createAgentApiV1AgentsPost(agentCreateRequest)

Create a new AI agent with specified configuration and capabilities.

### Example

```typescript
import {
    AgentsApi,
    Configuration,
    AgentCreateRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let agentCreateRequest: AgentCreateRequest; //

const { status, data } = await apiInstance.createAgentApiV1AgentsPost(
    agentCreateRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **agentCreateRequest** | **AgentCreateRequest**|  | |


### Return type

**AgentResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Agent created successfully |  -  |
|**400** | Invalid input data |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**404** | Not found |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createAgentApiV1AgentsPost_0**
> AgentResponse createAgentApiV1AgentsPost_0(agentCreateRequest)

Create a new AI agent with specified configuration and capabilities.

### Example

```typescript
import {
    AgentsApi,
    Configuration,
    AgentCreateRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let agentCreateRequest: AgentCreateRequest; //

const { status, data } = await apiInstance.createAgentApiV1AgentsPost_0(
    agentCreateRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **agentCreateRequest** | **AgentCreateRequest**|  | |


### Return type

**AgentResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Agent created successfully |  -  |
|**400** | Invalid input data |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**404** | Not found |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteAgentApiV1AgentsAgentIdDelete**
> AgentDeleteResponse deleteAgentApiV1AgentsAgentIdDelete()

Delete an agent.  Args:     agent_id: Agent ID     current_user: Current authenticated user     agent_manager: Agent manager instance  Returns:     Deletion result

### Example

```typescript
import {
    AgentsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let agentId: string; // (default to undefined)

const { status, data } = await apiInstance.deleteAgentApiV1AgentsAgentIdDelete(
    agentId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **agentId** | [**string**] |  | defaults to undefined|


### Return type

**AgentDeleteResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**400** | Bad request |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**404** | Not found |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteAgentApiV1AgentsAgentIdDelete_0**
> AgentDeleteResponse deleteAgentApiV1AgentsAgentIdDelete_0()

Delete an agent.  Args:     agent_id: Agent ID     current_user: Current authenticated user     agent_manager: Agent manager instance  Returns:     Deletion result

### Example

```typescript
import {
    AgentsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let agentId: string; // (default to undefined)

const { status, data } = await apiInstance.deleteAgentApiV1AgentsAgentIdDelete_0(
    agentId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **agentId** | [**string**] |  | defaults to undefined|


### Return type

**AgentDeleteResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**400** | Bad request |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**404** | Not found |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAgentApiV1AgentsAgentIdGet**
> AgentResponse getAgentApiV1AgentsAgentIdGet()

Get agent by ID.  Args:     agent_id: Agent ID     request: Get request parameters     current_user: Current authenticated user     agent_manager: Agent manager instance  Returns:     Agent data

### Example

```typescript
import {
    AgentsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let agentId: string; // (default to undefined)

const { status, data } = await apiInstance.getAgentApiV1AgentsAgentIdGet(
    agentId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **agentId** | [**string**] |  | defaults to undefined|


### Return type

**AgentResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**400** | Bad request |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**404** | Not found |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAgentApiV1AgentsAgentIdGet_0**
> AgentResponse getAgentApiV1AgentsAgentIdGet_0()

Get agent by ID.  Args:     agent_id: Agent ID     request: Get request parameters     current_user: Current authenticated user     agent_manager: Agent manager instance  Returns:     Agent data

### Example

```typescript
import {
    AgentsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let agentId: string; // (default to undefined)

const { status, data } = await apiInstance.getAgentApiV1AgentsAgentIdGet_0(
    agentId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **agentId** | [**string**] |  | defaults to undefined|


### Return type

**AgentResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**400** | Bad request |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**404** | Not found |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAgentHealthApiV1AgentsAgentIdHealthGet**
> AgentHealthResponse getAgentHealthApiV1AgentsAgentIdHealthGet()

Get agent health status.  Args:     agent_id: Agent ID     current_user: Current authenticated user     agent_manager: Agent manager instance  Returns:     Agent health information

### Example

```typescript
import {
    AgentsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let agentId: string; // (default to undefined)

const { status, data } = await apiInstance.getAgentHealthApiV1AgentsAgentIdHealthGet(
    agentId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **agentId** | [**string**] |  | defaults to undefined|


### Return type

**AgentHealthResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**400** | Bad request |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**404** | Not found |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAgentHealthApiV1AgentsAgentIdHealthGet_0**
> AgentHealthResponse getAgentHealthApiV1AgentsAgentIdHealthGet_0()

Get agent health status.  Args:     agent_id: Agent ID     current_user: Current authenticated user     agent_manager: Agent manager instance  Returns:     Agent health information

### Example

```typescript
import {
    AgentsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let agentId: string; // (default to undefined)

const { status, data } = await apiInstance.getAgentHealthApiV1AgentsAgentIdHealthGet_0(
    agentId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **agentId** | [**string**] |  | defaults to undefined|


### Return type

**AgentHealthResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**400** | Bad request |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**404** | Not found |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAgentStatsApiV1AgentsStatsOverviewGet**
> AgentStatsResponse getAgentStatsApiV1AgentsStatsOverviewGet()

Get comprehensive statistics about all agents for the current user.

### Example

```typescript
import {
    AgentsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

const { status, data } = await apiInstance.getAgentStatsApiV1AgentsStatsOverviewGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**AgentStatsResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**400** | Bad request |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**404** | Not found |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAgentStatsApiV1AgentsStatsOverviewGet_0**
> AgentStatsResponse getAgentStatsApiV1AgentsStatsOverviewGet_0()

Get comprehensive statistics about all agents for the current user.

### Example

```typescript
import {
    AgentsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

const { status, data } = await apiInstance.getAgentStatsApiV1AgentsStatsOverviewGet_0();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**AgentStatsResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**400** | Bad request |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**404** | Not found |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAgentTemplatesApiV1AgentsTemplatesGet**
> Array<{ [key: string]: any; }> getAgentTemplatesApiV1AgentsTemplatesGet()

Get predefined agent templates for common use cases.

### Example

```typescript
import {
    AgentsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

const { status, data } = await apiInstance.getAgentTemplatesApiV1AgentsTemplatesGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**Array<{ [key: string]: any; }>**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**400** | Bad request |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**404** | Not found |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAgentTemplatesApiV1AgentsTemplatesGet_0**
> Array<{ [key: string]: any; }> getAgentTemplatesApiV1AgentsTemplatesGet_0()

Get predefined agent templates for common use cases.

### Example

```typescript
import {
    AgentsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

const { status, data } = await apiInstance.getAgentTemplatesApiV1AgentsTemplatesGet_0();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**Array<{ [key: string]: any; }>**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**400** | Bad request |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**404** | Not found |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **interactWithAgentApiV1AgentsAgentIdInteractPost**
> AgentInteractResponse interactWithAgentApiV1AgentsAgentIdInteractPost(agentInteractRequest)

Send a message to an agent and receive a response. Rate limited per user per agent.

### Example

```typescript
import {
    AgentsApi,
    Configuration,
    AgentInteractRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let agentId: string; // (default to undefined)
let agentInteractRequest: AgentInteractRequest; //

const { status, data } = await apiInstance.interactWithAgentApiV1AgentsAgentIdInteractPost(
    agentId,
    agentInteractRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **agentInteractRequest** | **AgentInteractRequest**|  | |
| **agentId** | [**string**] |  | defaults to undefined|


### Return type

**AgentInteractResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Interaction successful |  -  |
|**400** | Bad request |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**404** | Agent not found or access denied |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **interactWithAgentApiV1AgentsAgentIdInteractPost_0**
> AgentInteractResponse interactWithAgentApiV1AgentsAgentIdInteractPost_0(agentInteractRequest)

Send a message to an agent and receive a response. Rate limited per user per agent.

### Example

```typescript
import {
    AgentsApi,
    Configuration,
    AgentInteractRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let agentId: string; // (default to undefined)
let agentInteractRequest: AgentInteractRequest; //

const { status, data } = await apiInstance.interactWithAgentApiV1AgentsAgentIdInteractPost_0(
    agentId,
    agentInteractRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **agentInteractRequest** | **AgentInteractRequest**|  | |
| **agentId** | [**string**] |  | defaults to undefined|


### Return type

**AgentInteractResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Interaction successful |  -  |
|**400** | Bad request |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**404** | Agent not found or access denied |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listAgentsApiV1AgentsGet**
> AgentListResponse listAgentsApiV1AgentsGet()

List all agents with optional filtering and pagination. Users can only see their own agents.

### Example

```typescript
import {
    AgentsApi,
    Configuration,
    BodyListAgentsApiV1AgentsGet
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let agentType: AgentType; // (optional) (default to undefined)
let status: AgentStatus; // (optional) (default to undefined)
let bodyListAgentsApiV1AgentsGet: BodyListAgentsApiV1AgentsGet; // (optional)

const { status, data } = await apiInstance.listAgentsApiV1AgentsGet(
    agentType,
    status,
    bodyListAgentsApiV1AgentsGet
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **bodyListAgentsApiV1AgentsGet** | **BodyListAgentsApiV1AgentsGet**|  | |
| **agentType** | **AgentType** |  | (optional) defaults to undefined|
| **status** | **AgentStatus** |  | (optional) defaults to undefined|


### Return type

**AgentListResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**400** | Bad request |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**404** | Not found |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listAgentsApiV1AgentsGet_0**
> AgentListResponse listAgentsApiV1AgentsGet_0()

List all agents with optional filtering and pagination. Users can only see their own agents.

### Example

```typescript
import {
    AgentsApi,
    Configuration,
    BodyListAgentsApiV1AgentsGet
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let agentType: AgentType; // (optional) (default to undefined)
let status: AgentStatus; // (optional) (default to undefined)
let bodyListAgentsApiV1AgentsGet: BodyListAgentsApiV1AgentsGet; // (optional)

const { status, data } = await apiInstance.listAgentsApiV1AgentsGet_0(
    agentType,
    status,
    bodyListAgentsApiV1AgentsGet
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **bodyListAgentsApiV1AgentsGet** | **BodyListAgentsApiV1AgentsGet**|  | |
| **agentType** | **AgentType** |  | (optional) defaults to undefined|
| **status** | **AgentStatus** |  | (optional) defaults to undefined|


### Return type

**AgentListResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**400** | Bad request |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**404** | Not found |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateAgentApiV1AgentsAgentIdPut**
> AgentResponse updateAgentApiV1AgentsAgentIdPut(agentUpdateRequest)

Update an agent.  Args:     agent_id: Agent ID     agent_data: Agent update data     current_user: Current authenticated user     agent_manager: Agent manager instance  Returns:     Updated agent data

### Example

```typescript
import {
    AgentsApi,
    Configuration,
    AgentUpdateRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let agentId: string; // (default to undefined)
let agentUpdateRequest: AgentUpdateRequest; //

const { status, data } = await apiInstance.updateAgentApiV1AgentsAgentIdPut(
    agentId,
    agentUpdateRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **agentUpdateRequest** | **AgentUpdateRequest**|  | |
| **agentId** | [**string**] |  | defaults to undefined|


### Return type

**AgentResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**400** | Bad request |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**404** | Not found |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateAgentApiV1AgentsAgentIdPut_0**
> AgentResponse updateAgentApiV1AgentsAgentIdPut_0(agentUpdateRequest)

Update an agent.  Args:     agent_id: Agent ID     agent_data: Agent update data     current_user: Current authenticated user     agent_manager: Agent manager instance  Returns:     Updated agent data

### Example

```typescript
import {
    AgentsApi,
    Configuration,
    AgentUpdateRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let agentId: string; // (default to undefined)
let agentUpdateRequest: AgentUpdateRequest; //

const { status, data } = await apiInstance.updateAgentApiV1AgentsAgentIdPut_0(
    agentId,
    agentUpdateRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **agentUpdateRequest** | **AgentUpdateRequest**|  | |
| **agentId** | [**string**] |  | defaults to undefined|


### Return type

**AgentResponse**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**400** | Bad request |  -  |
|**401** | Unauthorized |  -  |
|**403** | Forbidden |  -  |
|**404** | Not found |  -  |
|**429** | Rate limit exceeded |  -  |
|**500** | Internal server error |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

