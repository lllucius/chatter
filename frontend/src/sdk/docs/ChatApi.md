# ChatApi

All URIs are relative to *http://localhost:8000*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**chatApiV1ChatChatPost**](#chatapiv1chatchatpost) | **POST** /api/v1/chat/chat | Chat|
|[**chatWithTemplateApiV1ChatTemplateTemplateNamePost**](#chatwithtemplateapiv1chattemplatetemplatenamepost) | **POST** /api/v1/chat/template/{template_name} | Chat With Template|
|[**createConversationApiV1ChatConversationsPost**](#createconversationapiv1chatconversationspost) | **POST** /api/v1/chat/conversations | Create Conversation|
|[**deleteConversationApiV1ChatConversationsConversationIdDelete**](#deleteconversationapiv1chatconversationsconversationiddelete) | **DELETE** /api/v1/chat/conversations/{conversation_id} | Delete Conversation|
|[**deleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDelete**](#deletemessageapiv1chatconversationsconversationidmessagesmessageiddelete) | **DELETE** /api/v1/chat/conversations/{conversation_id}/messages/{message_id} | Delete Message|
|[**getAvailableToolsApiV1ChatToolsAvailableGet**](#getavailabletoolsapiv1chattoolsavailableget) | **GET** /api/v1/chat/tools/available | Get Available Tools|
|[**getConversationApiV1ChatConversationsConversationIdGet**](#getconversationapiv1chatconversationsconversationidget) | **GET** /api/v1/chat/conversations/{conversation_id} | Get Conversation|
|[**getConversationMessagesApiV1ChatConversationsConversationIdMessagesGet**](#getconversationmessagesapiv1chatconversationsconversationidmessagesget) | **GET** /api/v1/chat/conversations/{conversation_id}/messages | Get Conversation Messages|
|[**getMcpStatusApiV1ChatMcpStatusGet**](#getmcpstatusapiv1chatmcpstatusget) | **GET** /api/v1/chat/mcp/status | Get Mcp Status|
|[**getPerformanceStatsApiV1ChatPerformanceStatsGet**](#getperformancestatsapiv1chatperformancestatsget) | **GET** /api/v1/chat/performance/stats | Get Performance Stats|
|[**getWorkflowTemplatesApiV1ChatTemplatesGet**](#getworkflowtemplatesapiv1chattemplatesget) | **GET** /api/v1/chat/templates | Get Workflow Templates|
|[**listConversationsApiV1ChatConversationsGet**](#listconversationsapiv1chatconversationsget) | **GET** /api/v1/chat/conversations | List Conversations|
|[**updateConversationApiV1ChatConversationsConversationIdPut**](#updateconversationapiv1chatconversationsconversationidput) | **PUT** /api/v1/chat/conversations/{conversation_id} | Update Conversation|

# **chatApiV1ChatChatPost**
> ChatResponse1 chatApiV1ChatChatPost(chatRequest)

Unified chat endpoint supporting all workflow types with optional streaming.

### Example

```typescript
import {
    ChatApi,
    Configuration,
    ChatRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ChatApi(configuration);

let chatRequest: ChatRequest; //

const { status, data } = await apiInstance.chatApiV1ChatChatPost(
    chatRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **chatRequest** | **ChatRequest**|  | |


### Return type

**ChatResponse1**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/event-stream


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Chat response as JSON or streaming SSE when stream&#x3D;true |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **chatWithTemplateApiV1ChatTemplateTemplateNamePost**
> ChatResponse chatWithTemplateApiV1ChatTemplateTemplateNamePost(chatRequest)

Chat using a specific workflow template.

### Example

```typescript
import {
    ChatApi,
    Configuration,
    ChatRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ChatApi(configuration);

let templateName: string; // (default to undefined)
let chatRequest: ChatRequest; //

const { status, data } = await apiInstance.chatWithTemplateApiV1ChatTemplateTemplateNamePost(
    templateName,
    chatRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **chatRequest** | **ChatRequest**|  | |
| **templateName** | [**string**] |  | defaults to undefined|


### Return type

**ChatResponse**

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

# **createConversationApiV1ChatConversationsPost**
> ConversationResponse createConversationApiV1ChatConversationsPost(conversationCreate)

Create a new conversation.

### Example

```typescript
import {
    ChatApi,
    Configuration,
    ConversationCreate
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ChatApi(configuration);

let conversationCreate: ConversationCreate; //

const { status, data } = await apiInstance.createConversationApiV1ChatConversationsPost(
    conversationCreate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **conversationCreate** | **ConversationCreate**|  | |


### Return type

**ConversationResponse**

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

# **deleteConversationApiV1ChatConversationsConversationIdDelete**
> ConversationDeleteResponse deleteConversationApiV1ChatConversationsConversationIdDelete()

Delete conversation.

### Example

```typescript
import {
    ChatApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ChatApi(configuration);

let conversationId: string; //Conversation ID (default to undefined)

const { status, data } = await apiInstance.deleteConversationApiV1ChatConversationsConversationIdDelete(
    conversationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **conversationId** | [**string**] | Conversation ID | defaults to undefined|


### Return type

**ConversationDeleteResponse**

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

# **deleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDelete**
> MessageDeleteResponse deleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDelete()

Delete a message from a conversation.

### Example

```typescript
import {
    ChatApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ChatApi(configuration);

let conversationId: string; //Conversation ID (default to undefined)
let messageId: string; //Message ID (default to undefined)

const { status, data } = await apiInstance.deleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDelete(
    conversationId,
    messageId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **conversationId** | [**string**] | Conversation ID | defaults to undefined|
| **messageId** | [**string**] | Message ID | defaults to undefined|


### Return type

**MessageDeleteResponse**

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

# **getAvailableToolsApiV1ChatToolsAvailableGet**
> AvailableToolsResponse getAvailableToolsApiV1ChatToolsAvailableGet()

Get list of available MCP tools.

### Example

```typescript
import {
    ChatApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ChatApi(configuration);

const { status, data } = await apiInstance.getAvailableToolsApiV1ChatToolsAvailableGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**AvailableToolsResponse**

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

# **getConversationApiV1ChatConversationsConversationIdGet**
> ConversationWithMessages getConversationApiV1ChatConversationsConversationIdGet()

Get conversation details with optional messages.

### Example

```typescript
import {
    ChatApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ChatApi(configuration);

let conversationId: string; //Conversation ID (default to undefined)
let includeMessages: boolean; //Include messages in response (optional) (default to true)

const { status, data } = await apiInstance.getConversationApiV1ChatConversationsConversationIdGet(
    conversationId,
    includeMessages
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **conversationId** | [**string**] | Conversation ID | defaults to undefined|
| **includeMessages** | [**boolean**] | Include messages in response | (optional) defaults to true|


### Return type

**ConversationWithMessages**

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

# **getConversationMessagesApiV1ChatConversationsConversationIdMessagesGet**
> Array<MessageResponse> getConversationMessagesApiV1ChatConversationsConversationIdMessagesGet()

Get messages from a conversation.

### Example

```typescript
import {
    ChatApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ChatApi(configuration);

let conversationId: string; //Conversation ID (default to undefined)
let limit: number; //Number of results per page (optional) (default to 50)
let offset: number; //Number of results to skip (optional) (default to 0)

const { status, data } = await apiInstance.getConversationMessagesApiV1ChatConversationsConversationIdMessagesGet(
    conversationId,
    limit,
    offset
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **conversationId** | [**string**] | Conversation ID | defaults to undefined|
| **limit** | [**number**] | Number of results per page | (optional) defaults to 50|
| **offset** | [**number**] | Number of results to skip | (optional) defaults to 0|


### Return type

**Array<MessageResponse>**

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

# **getMcpStatusApiV1ChatMcpStatusGet**
> McpStatusResponse getMcpStatusApiV1ChatMcpStatusGet()

Get MCP service status.

### Example

```typescript
import {
    ChatApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ChatApi(configuration);

const { status, data } = await apiInstance.getMcpStatusApiV1ChatMcpStatusGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**McpStatusResponse**

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

# **getPerformanceStatsApiV1ChatPerformanceStatsGet**
> PerformanceStatsResponse getPerformanceStatsApiV1ChatPerformanceStatsGet()

Get workflow performance statistics.

### Example

```typescript
import {
    ChatApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ChatApi(configuration);

const { status, data } = await apiInstance.getPerformanceStatsApiV1ChatPerformanceStatsGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**PerformanceStatsResponse**

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

# **getWorkflowTemplatesApiV1ChatTemplatesGet**
> WorkflowTemplatesResponse getWorkflowTemplatesApiV1ChatTemplatesGet()

Get available workflow templates.

### Example

```typescript
import {
    ChatApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ChatApi(configuration);

const { status, data } = await apiInstance.getWorkflowTemplatesApiV1ChatTemplatesGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**WorkflowTemplatesResponse**

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

# **listConversationsApiV1ChatConversationsGet**
> ConversationSearchResponse listConversationsApiV1ChatConversationsGet()

List conversations for the current user.

### Example

```typescript
import {
    ChatApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ChatApi(configuration);

let limit: number; //Number of results per page (optional) (default to 20)
let offset: number; //Number of results to skip (optional) (default to 0)

const { status, data } = await apiInstance.listConversationsApiV1ChatConversationsGet(
    limit,
    offset
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **limit** | [**number**] | Number of results per page | (optional) defaults to 20|
| **offset** | [**number**] | Number of results to skip | (optional) defaults to 0|


### Return type

**ConversationSearchResponse**

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

# **updateConversationApiV1ChatConversationsConversationIdPut**
> ConversationResponse updateConversationApiV1ChatConversationsConversationIdPut(conversationUpdate)

Update conversation.

### Example

```typescript
import {
    ChatApi,
    Configuration,
    ConversationUpdate
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ChatApi(configuration);

let conversationId: string; //Conversation ID (default to undefined)
let conversationUpdate: ConversationUpdate; //

const { status, data } = await apiInstance.updateConversationApiV1ChatConversationsConversationIdPut(
    conversationId,
    conversationUpdate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **conversationUpdate** | **ConversationUpdate**|  | |
| **conversationId** | [**string**] | Conversation ID | defaults to undefined|


### Return type

**ConversationResponse**

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

