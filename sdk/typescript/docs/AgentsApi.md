# AgentsApi

All URIs are relative to *http://localhost:8000*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**bulkCreateAgentsApiV1AgentsAgentsBulkPost**](#bulkcreateagentsapiv1agentsagentsbulkpost) | **POST** /api/v1/agents/agents/bulk | Bulk Create Agents|
|[**bulkCreateAgentsApiV1AgentsAgentsBulkPost_0**](#bulkcreateagentsapiv1agentsagentsbulkpost_0) | **POST** /api/v1/agents/agents/bulk | Bulk Create Agents|
|[**bulkDeleteAgentsApiV1AgentsAgentsBulkDelete**](#bulkdeleteagentsapiv1agentsagentsbulkdelete) | **DELETE** /api/v1/agents/agents/bulk | Bulk Delete Agents|
|[**bulkDeleteAgentsApiV1AgentsAgentsBulkDelete_0**](#bulkdeleteagentsapiv1agentsagentsbulkdelete_0) | **DELETE** /api/v1/agents/agents/bulk | Bulk Delete Agents|
|[**createAgentApiV1AgentsAgentsPost**](#createagentapiv1agentsagentspost) | **POST** /api/v1/agents/agents/ | Create a new agent|
|[**createAgentApiV1AgentsAgentsPost_0**](#createagentapiv1agentsagentspost_0) | **POST** /api/v1/agents/agents/ | Create a new agent|
|[**deleteAgentApiV1AgentsAgentsAgentIdDelete**](#deleteagentapiv1agentsagentsagentiddelete) | **DELETE** /api/v1/agents/agents/{agent_id} | Delete Agent|
|[**deleteAgentApiV1AgentsAgentsAgentIdDelete_0**](#deleteagentapiv1agentsagentsagentiddelete_0) | **DELETE** /api/v1/agents/agents/{agent_id} | Delete Agent|
|[**getAgentApiV1AgentsAgentsAgentIdGet**](#getagentapiv1agentsagentsagentidget) | **GET** /api/v1/agents/agents/{agent_id} | Get Agent|
|[**getAgentApiV1AgentsAgentsAgentIdGet_0**](#getagentapiv1agentsagentsagentidget_0) | **GET** /api/v1/agents/agents/{agent_id} | Get Agent|
|[**getAgentHealthApiV1AgentsAgentsAgentIdHealthGet**](#getagenthealthapiv1agentsagentsagentidhealthget) | **GET** /api/v1/agents/agents/{agent_id}/health | Get Agent Health|
|[**getAgentHealthApiV1AgentsAgentsAgentIdHealthGet_0**](#getagenthealthapiv1agentsagentsagentidhealthget_0) | **GET** /api/v1/agents/agents/{agent_id}/health | Get Agent Health|
|[**getAgentStatsApiV1AgentsAgentsStatsOverviewGet**](#getagentstatsapiv1agentsagentsstatsoverviewget) | **GET** /api/v1/agents/agents/stats/overview | Get agent statistics|
|[**getAgentStatsApiV1AgentsAgentsStatsOverviewGet_0**](#getagentstatsapiv1agentsagentsstatsoverviewget_0) | **GET** /api/v1/agents/agents/stats/overview | Get agent statistics|
|[**interactWithAgentApiV1AgentsAgentsAgentIdInteractPost**](#interactwithagentapiv1agentsagentsagentidinteractpost) | **POST** /api/v1/agents/agents/{agent_id}/interact | Interact with agent|
|[**interactWithAgentApiV1AgentsAgentsAgentIdInteractPost_0**](#interactwithagentapiv1agentsagentsagentidinteractpost_0) | **POST** /api/v1/agents/agents/{agent_id}/interact | Interact with agent|
|[**listAgentsApiV1AgentsAgentsGet**](#listagentsapiv1agentsagentsget) | **GET** /api/v1/agents/agents/ | List agents|
|[**listAgentsApiV1AgentsAgentsGet_0**](#listagentsapiv1agentsagentsget_0) | **GET** /api/v1/agents/agents/ | List agents|
|[**updateAgentApiV1AgentsAgentsAgentIdPut**](#updateagentapiv1agentsagentsagentidput) | **PUT** /api/v1/agents/agents/{agent_id} | Update Agent|
|[**updateAgentApiV1AgentsAgentsAgentIdPut_0**](#updateagentapiv1agentsagentsagentidput_0) | **PUT** /api/v1/agents/agents/{agent_id} | Update Agent|

# **bulkCreateAgentsApiV1AgentsAgentsBulkPost**
> AgentBulkCreateResponse bulkCreateAgentsApiV1AgentsAgentsBulkPost(agentBulkCreateRequest)

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

const { status, data } = await apiInstance.bulkCreateAgentsApiV1AgentsAgentsBulkPost(
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

[HTTPBearer](../README.md#HTTPBearer)

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

# **bulkCreateAgentsApiV1AgentsAgentsBulkPost_0**
> AgentBulkCreateResponse bulkCreateAgentsApiV1AgentsAgentsBulkPost_0(agentBulkCreateRequest)

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

const { status, data } = await apiInstance.bulkCreateAgentsApiV1AgentsAgentsBulkPost_0(
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

[HTTPBearer](../README.md#HTTPBearer)

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

# **bulkDeleteAgentsApiV1AgentsAgentsBulkDelete**
> { [key: string]: any; } bulkDeleteAgentsApiV1AgentsAgentsBulkDelete(agentBulkDeleteRequest)

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

const { status, data } = await apiInstance.bulkDeleteAgentsApiV1AgentsAgentsBulkDelete(
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

[HTTPBearer](../README.md#HTTPBearer)

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

# **bulkDeleteAgentsApiV1AgentsAgentsBulkDelete_0**
> { [key: string]: any; } bulkDeleteAgentsApiV1AgentsAgentsBulkDelete_0(agentBulkDeleteRequest)

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

const { status, data } = await apiInstance.bulkDeleteAgentsApiV1AgentsAgentsBulkDelete_0(
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

[HTTPBearer](../README.md#HTTPBearer)

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

# **createAgentApiV1AgentsAgentsPost**
> AgentResponse createAgentApiV1AgentsAgentsPost(agentCreateRequest)

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

const { status, data } = await apiInstance.createAgentApiV1AgentsAgentsPost(
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

[HTTPBearer](../README.md#HTTPBearer)

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

# **createAgentApiV1AgentsAgentsPost_0**
> AgentResponse createAgentApiV1AgentsAgentsPost_0(agentCreateRequest)

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

const { status, data } = await apiInstance.createAgentApiV1AgentsAgentsPost_0(
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

[HTTPBearer](../README.md#HTTPBearer)

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

# **deleteAgentApiV1AgentsAgentsAgentIdDelete**
> AgentDeleteResponse deleteAgentApiV1AgentsAgentsAgentIdDelete()

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

const { status, data } = await apiInstance.deleteAgentApiV1AgentsAgentsAgentIdDelete(
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

[HTTPBearer](../README.md#HTTPBearer)

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

# **deleteAgentApiV1AgentsAgentsAgentIdDelete_0**
> AgentDeleteResponse deleteAgentApiV1AgentsAgentsAgentIdDelete_0()

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

const { status, data } = await apiInstance.deleteAgentApiV1AgentsAgentsAgentIdDelete_0(
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

[HTTPBearer](../README.md#HTTPBearer)

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

# **getAgentApiV1AgentsAgentsAgentIdGet**
> AgentResponse getAgentApiV1AgentsAgentsAgentIdGet()

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

const { status, data } = await apiInstance.getAgentApiV1AgentsAgentsAgentIdGet(
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

[HTTPBearer](../README.md#HTTPBearer)

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

# **getAgentApiV1AgentsAgentsAgentIdGet_0**
> AgentResponse getAgentApiV1AgentsAgentsAgentIdGet_0()

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

const { status, data } = await apiInstance.getAgentApiV1AgentsAgentsAgentIdGet_0(
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

[HTTPBearer](../README.md#HTTPBearer)

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

# **getAgentHealthApiV1AgentsAgentsAgentIdHealthGet**
> AgentHealthResponse getAgentHealthApiV1AgentsAgentsAgentIdHealthGet()

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

const { status, data } = await apiInstance.getAgentHealthApiV1AgentsAgentsAgentIdHealthGet(
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

[HTTPBearer](../README.md#HTTPBearer)

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

# **getAgentHealthApiV1AgentsAgentsAgentIdHealthGet_0**
> AgentHealthResponse getAgentHealthApiV1AgentsAgentsAgentIdHealthGet_0()

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

const { status, data } = await apiInstance.getAgentHealthApiV1AgentsAgentsAgentIdHealthGet_0(
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

[HTTPBearer](../README.md#HTTPBearer)

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

# **getAgentStatsApiV1AgentsAgentsStatsOverviewGet**
> AgentStatsResponse getAgentStatsApiV1AgentsAgentsStatsOverviewGet()

Get comprehensive statistics about all agents for the current user.

### Example

```typescript
import {
    AgentsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

const { status, data } = await apiInstance.getAgentStatsApiV1AgentsAgentsStatsOverviewGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**AgentStatsResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

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

# **getAgentStatsApiV1AgentsAgentsStatsOverviewGet_0**
> AgentStatsResponse getAgentStatsApiV1AgentsAgentsStatsOverviewGet_0()

Get comprehensive statistics about all agents for the current user.

### Example

```typescript
import {
    AgentsApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

const { status, data } = await apiInstance.getAgentStatsApiV1AgentsAgentsStatsOverviewGet_0();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**AgentStatsResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

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

# **interactWithAgentApiV1AgentsAgentsAgentIdInteractPost**
> AgentInteractResponse interactWithAgentApiV1AgentsAgentsAgentIdInteractPost(agentInteractRequest)

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

const { status, data } = await apiInstance.interactWithAgentApiV1AgentsAgentsAgentIdInteractPost(
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

[HTTPBearer](../README.md#HTTPBearer)

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

# **interactWithAgentApiV1AgentsAgentsAgentIdInteractPost_0**
> AgentInteractResponse interactWithAgentApiV1AgentsAgentsAgentIdInteractPost_0(agentInteractRequest)

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

const { status, data } = await apiInstance.interactWithAgentApiV1AgentsAgentsAgentIdInteractPost_0(
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

[HTTPBearer](../README.md#HTTPBearer)

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

# **listAgentsApiV1AgentsAgentsGet**
> AgentListResponse listAgentsApiV1AgentsAgentsGet()

List all agents with optional filtering and pagination. Users can only see their own agents.

### Example

```typescript
import {
    AgentsApi,
    Configuration,
    BodyListAgentsApiV1AgentsAgentsGet
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let agentType: AgentType; // (optional) (default to undefined)
let status: AgentStatus; // (optional) (default to undefined)
let bodyListAgentsApiV1AgentsAgentsGet: BodyListAgentsApiV1AgentsAgentsGet; // (optional)

const { status, data } = await apiInstance.listAgentsApiV1AgentsAgentsGet(
    agentType,
    status,
    bodyListAgentsApiV1AgentsAgentsGet
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **bodyListAgentsApiV1AgentsAgentsGet** | **BodyListAgentsApiV1AgentsAgentsGet**|  | |
| **agentType** | **AgentType** |  | (optional) defaults to undefined|
| **status** | **AgentStatus** |  | (optional) defaults to undefined|


### Return type

**AgentListResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

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

# **listAgentsApiV1AgentsAgentsGet_0**
> AgentListResponse listAgentsApiV1AgentsAgentsGet_0()

List all agents with optional filtering and pagination. Users can only see their own agents.

### Example

```typescript
import {
    AgentsApi,
    Configuration,
    BodyListAgentsApiV1AgentsAgentsGet
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new AgentsApi(configuration);

let agentType: AgentType; // (optional) (default to undefined)
let status: AgentStatus; // (optional) (default to undefined)
let bodyListAgentsApiV1AgentsAgentsGet: BodyListAgentsApiV1AgentsAgentsGet; // (optional)

const { status, data } = await apiInstance.listAgentsApiV1AgentsAgentsGet_0(
    agentType,
    status,
    bodyListAgentsApiV1AgentsAgentsGet
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **bodyListAgentsApiV1AgentsAgentsGet** | **BodyListAgentsApiV1AgentsAgentsGet**|  | |
| **agentType** | **AgentType** |  | (optional) defaults to undefined|
| **status** | **AgentStatus** |  | (optional) defaults to undefined|


### Return type

**AgentListResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

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

# **updateAgentApiV1AgentsAgentsAgentIdPut**
> AgentResponse updateAgentApiV1AgentsAgentsAgentIdPut(agentUpdateRequest)

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

const { status, data } = await apiInstance.updateAgentApiV1AgentsAgentsAgentIdPut(
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

[HTTPBearer](../README.md#HTTPBearer)

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

# **updateAgentApiV1AgentsAgentsAgentIdPut_0**
> AgentResponse updateAgentApiV1AgentsAgentsAgentIdPut_0(agentUpdateRequest)

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

const { status, data } = await apiInstance.updateAgentApiV1AgentsAgentsAgentIdPut_0(
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

[HTTPBearer](../README.md#HTTPBearer)

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

