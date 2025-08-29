# AgentsApi

All URIs are relative to *http://localhost:8000*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**createAgentApiV1AgentsPost**](#createagentapiv1agentspost) | **POST** /api/v1/agents/ | Create Agent|
|[**deleteAgentApiV1AgentsAgentIdDelete**](#deleteagentapiv1agentsagentiddelete) | **DELETE** /api/v1/agents/{agent_id} | Delete Agent|
|[**getAgentApiV1AgentsAgentIdGet**](#getagentapiv1agentsagentidget) | **GET** /api/v1/agents/{agent_id} | Get Agent|
|[**getAgentStatsApiV1AgentsStatsOverviewGet**](#getagentstatsapiv1agentsstatsoverviewget) | **GET** /api/v1/agents/stats/overview | Get Agent Stats|
|[**interactWithAgentApiV1AgentsAgentIdInteractPost**](#interactwithagentapiv1agentsagentidinteractpost) | **POST** /api/v1/agents/{agent_id}/interact | Interact With Agent|
|[**listAgentsApiV1AgentsGet**](#listagentsapiv1agentsget) | **GET** /api/v1/agents/ | List Agents|
|[**updateAgentApiV1AgentsAgentIdPut**](#updateagentapiv1agentsagentidput) | **PUT** /api/v1/agents/{agent_id} | Update Agent|

# **createAgentApiV1AgentsPost**
> AgentResponse createAgentApiV1AgentsPost(agentCreateRequest)

Create a new agent.  Args:     agent_data: Agent creation data     current_user: Current authenticated user     agent_manager: Agent manager instance  Returns:     Created agent data

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

# **getAgentStatsApiV1AgentsStatsOverviewGet**
> AgentStatsResponse getAgentStatsApiV1AgentsStatsOverviewGet()

Get agent statistics.  Args:     current_user: Current authenticated user     agent_manager: Agent manager instance  Returns:     Agent statistics

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

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **interactWithAgentApiV1AgentsAgentIdInteractPost**
> AgentInteractResponse interactWithAgentApiV1AgentsAgentIdInteractPost(agentInteractRequest)

Send a message to an agent and get a response.  Args:     agent_id: Agent ID     interaction_data: Interaction data     current_user: Current authenticated user     agent_manager: Agent manager instance  Returns:     Agent response

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

# **listAgentsApiV1AgentsGet**
> AgentListResponse listAgentsApiV1AgentsGet()

List all agents with optional filtering and pagination.  Args:     request: List request parameters with pagination     current_user: Current authenticated user     agent_manager: Agent manager instance  Returns:     Paginated list of agents

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

