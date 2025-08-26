# ChatApi

All URIs are relative to *http://localhost:8000*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**addMessageToConversationApiV1ChatConversationsConversationIdMessagesPost**](#addmessagetoconversationapiv1chatconversationsconversationidmessagespost) | **POST** /api/v1/chat/conversations/{conversation_id}/messages | Add Message To Conversation|
|[**chatApiV1ChatChatPost**](#chatapiv1chatchatpost) | **POST** /api/v1/chat/chat | Chat|
|[**createConversationApiV1ChatConversationsPost**](#createconversationapiv1chatconversationspost) | **POST** /api/v1/chat/conversations | Create Conversation|
|[**deleteConversationApiV1ChatConversationsConversationIdDelete**](#deleteconversationapiv1chatconversationsconversationiddelete) | **DELETE** /api/v1/chat/conversations/{conversation_id} | Delete Conversation|
|[**deleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDelete**](#deletemessageapiv1chatconversationsconversationidmessagesmessageiddelete) | **DELETE** /api/v1/chat/conversations/{conversation_id}/messages/{message_id} | Delete Message|
|[**getAvailableToolsApiV1ChatToolsAvailableGet**](#getavailabletoolsapiv1chattoolsavailableget) | **GET** /api/v1/chat/tools/available | Get Available Tools|
|[**getConversationApiV1ChatConversationsConversationIdGet**](#getconversationapiv1chatconversationsconversationidget) | **GET** /api/v1/chat/conversations/{conversation_id} | Get Conversation|
|[**getConversationMessagesApiV1ChatConversationsConversationIdMessagesGet**](#getconversationmessagesapiv1chatconversationsconversationidmessagesget) | **GET** /api/v1/chat/conversations/{conversation_id}/messages | Get Conversation Messages|
|[**getMcpStatusApiV1ChatMcpStatusGet**](#getmcpstatusapiv1chatmcpstatusget) | **GET** /api/v1/chat/mcp/status | Get Mcp Status|
|[**listConversationsApiV1ChatConversationsGet**](#listconversationsapiv1chatconversationsget) | **GET** /api/v1/chat/conversations | List Conversations|
|[**updateConversationApiV1ChatConversationsConversationIdPut**](#updateconversationapiv1chatconversationsconversationidput) | **PUT** /api/v1/chat/conversations/{conversation_id} | Update Conversation|

# **addMessageToConversationApiV1ChatConversationsConversationIdMessagesPost**
> MessageResponse addMessageToConversationApiV1ChatConversationsConversationIdMessagesPost(messageCreate)

Add a new message to existing conversation.

### Example

```typescript
import {
    ChatApi,
    Configuration,
    MessageCreate
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ChatApi(configuration);

let conversationId: string; // (default to undefined)
let messageCreate: MessageCreate; //

const { status, data } = await apiInstance.addMessageToConversationApiV1ChatConversationsConversationIdMessagesPost(
    conversationId,
    messageCreate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **messageCreate** | **MessageCreate**|  | |
| **conversationId** | [**string**] |  | defaults to undefined|


### Return type

**MessageResponse**

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

# **chatApiV1ChatChatPost**
> ChatResponse chatApiV1ChatChatPost(chatRequest)

Single chat endpoint supporting plain, rag, tools, and full workflows.  - If chat_request.stream is True, returns SSE stream. - Otherwise returns ChatResponse JSON.

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

**ChatResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/event-stream


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Chat response as JSON or streaming SSE when stream&#x3D;true |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createConversationApiV1ChatConversationsPost**
> ConversationResponse createConversationApiV1ChatConversationsPost(conversationCreate)

Create a new conversation.  Args:     conversation_data: Conversation creation data     current_user: Current authenticated user     chat_service: Chat service  Returns:     Created conversation

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

let conversationId: string; // (default to undefined)

const { status, data } = await apiInstance.deleteConversationApiV1ChatConversationsConversationIdDelete(
    conversationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **conversationId** | [**string**] |  | defaults to undefined|


### Return type

**ConversationDeleteResponse**

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

# **deleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDelete**
> { [key: string]: any; } deleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDelete()

Delete a message from conversation.

### Example

```typescript
import {
    ChatApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ChatApi(configuration);

let conversationId: string; // (default to undefined)
let messageId: string; // (default to undefined)

const { status, data } = await apiInstance.deleteMessageApiV1ChatConversationsConversationIdMessagesMessageIdDelete(
    conversationId,
    messageId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **conversationId** | [**string**] |  | defaults to undefined|
| **messageId** | [**string**] |  | defaults to undefined|


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

[HTTPBearer](../README.md#HTTPBearer)

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

Get conversation details with messages.

### Example

```typescript
import {
    ChatApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ChatApi(configuration);

let conversationId: string; // (default to undefined)

const { status, data } = await apiInstance.getConversationApiV1ChatConversationsConversationIdGet(
    conversationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **conversationId** | [**string**] |  | defaults to undefined|


### Return type

**ConversationWithMessages**

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

# **getConversationMessagesApiV1ChatConversationsConversationIdMessagesGet**
> Array<MessageResponse> getConversationMessagesApiV1ChatConversationsConversationIdMessagesGet()

Get conversation messages.

### Example

```typescript
import {
    ChatApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ChatApi(configuration);

let conversationId: string; // (default to undefined)

const { status, data } = await apiInstance.getConversationMessagesApiV1ChatConversationsConversationIdMessagesGet(
    conversationId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **conversationId** | [**string**] |  | defaults to undefined|


### Return type

**Array<MessageResponse>**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**401** | Unauthorized - Invalid or missing authentication token |  -  |
|**403** | Forbidden - User lacks permission to access this conversation |  -  |
|**404** | Not Found - Conversation does not exist |  -  |
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

[HTTPBearer](../README.md#HTTPBearer)

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

List user\'s conversations.  Note: Filters may be ignored if not supported by the service implementation.

### Example

```typescript
import {
    ChatApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ChatApi(configuration);

let query: string; //Search query (optional) (default to undefined)
let status: ConversationStatus; //Filter by status (optional) (default to undefined)
let limit: number; //Maximum number of results (optional) (default to 50)
let offset: number; //Number of results to skip (optional) (default to 0)
let sortBy: string; //Sort field (optional) (default to 'created_at')
let sortOrder: string; //Sort order (optional) (default to 'desc')

const { status, data } = await apiInstance.listConversationsApiV1ChatConversationsGet(
    query,
    status,
    limit,
    offset,
    sortBy,
    sortOrder
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **query** | [**string**] | Search query | (optional) defaults to undefined|
| **status** | **ConversationStatus** | Filter by status | (optional) defaults to undefined|
| **limit** | [**number**] | Maximum number of results | (optional) defaults to 50|
| **offset** | [**number**] | Number of results to skip | (optional) defaults to 0|
| **sortBy** | [**string**] | Sort field | (optional) defaults to 'created_at'|
| **sortOrder** | [**string**] | Sort order | (optional) defaults to 'desc'|


### Return type

**ConversationSearchResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**401** | Unauthorized - Invalid or missing authentication token |  -  |
|**403** | Forbidden - User lacks permission to access conversations |  -  |
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

let conversationId: string; // (default to undefined)
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
| **conversationId** | [**string**] |  | defaults to undefined|


### Return type

**ConversationResponse**

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

