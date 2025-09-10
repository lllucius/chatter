# chatter_sdk.ChatApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**chat_api_v1_chat_chat_post**](ChatApi.md#chat_api_v1_chat_chat_post) | **POST** /api/v1/chat/chat | Chat
[**chat_with_template_api_v1_chat_template_template_name_post**](ChatApi.md#chat_with_template_api_v1_chat_template_template_name_post) | **POST** /api/v1/chat/template/{template_name} | Chat With Template
[**create_conversation_api_v1_chat_conversations_post**](ChatApi.md#create_conversation_api_v1_chat_conversations_post) | **POST** /api/v1/chat/conversations | Create Conversation
[**delete_conversation_api_v1_chat_conversations_conversation_id_delete**](ChatApi.md#delete_conversation_api_v1_chat_conversations_conversation_id_delete) | **DELETE** /api/v1/chat/conversations/{conversation_id} | Delete Conversation
[**delete_message_api_v1_chat_conversations_conversation_id_messages_message_id_delete**](ChatApi.md#delete_message_api_v1_chat_conversations_conversation_id_messages_message_id_delete) | **DELETE** /api/v1/chat/conversations/{conversation_id}/messages/{message_id} | Delete Message
[**get_available_tools_api_v1_chat_tools_available_get**](ChatApi.md#get_available_tools_api_v1_chat_tools_available_get) | **GET** /api/v1/chat/tools/available | Get Available Tools
[**get_conversation_api_v1_chat_conversations_conversation_id_get**](ChatApi.md#get_conversation_api_v1_chat_conversations_conversation_id_get) | **GET** /api/v1/chat/conversations/{conversation_id} | Get Conversation
[**get_conversation_messages_api_v1_chat_conversations_conversation_id_messages_get**](ChatApi.md#get_conversation_messages_api_v1_chat_conversations_conversation_id_messages_get) | **GET** /api/v1/chat/conversations/{conversation_id}/messages | Get Conversation Messages
[**get_mcp_status_api_v1_chat_mcp_status_get**](ChatApi.md#get_mcp_status_api_v1_chat_mcp_status_get) | **GET** /api/v1/chat/mcp/status | Get Mcp Status
[**get_performance_stats_api_v1_chat_performance_stats_get**](ChatApi.md#get_performance_stats_api_v1_chat_performance_stats_get) | **GET** /api/v1/chat/performance/stats | Get Performance Stats
[**get_workflow_templates_api_v1_chat_templates_get**](ChatApi.md#get_workflow_templates_api_v1_chat_templates_get) | **GET** /api/v1/chat/templates | Get Workflow Templates
[**list_conversations_api_v1_chat_conversations_get**](ChatApi.md#list_conversations_api_v1_chat_conversations_get) | **GET** /api/v1/chat/conversations | List Conversations
[**streaming_chat_api_v1_chat_streaming_post**](ChatApi.md#streaming_chat_api_v1_chat_streaming_post) | **POST** /api/v1/chat/streaming | Streaming Chat
[**update_conversation_api_v1_chat_conversations_conversation_id_put**](ChatApi.md#update_conversation_api_v1_chat_conversations_conversation_id_put) | **PUT** /api/v1/chat/conversations/{conversation_id} | Update Conversation


# **chat_api_v1_chat_chat_post**
> ChatResponse chat_api_v1_chat_chat_post(chat_request)

Chat

Non-streaming chat endpoint supporting all workflow types.
## Workflow Types

This endpoint supports multiple workflow types through the `workflow` parameter:

### Plain Chat (`plain`)
Basic conversation without tools or retrieval.
```json
{
    "message": "Hello, how are you?",
    "workflow": "plain"
}
```

### RAG Workflow (`rag`)
Retrieval-Augmented Generation with document search.
```json
{
    "message": "What are the latest sales figures?",
    "workflow": "rag",
    "enable_retrieval": true
}
```

### Tools Workflow (`tools`)
Function calling with available tools.
```json
{
    "message": "Calculate the square root of 144",
    "workflow": "tools"
}
```

### Full Workflow (`full`)
Combination of RAG and tools for complex tasks.
```json
{
    "message": "Find recent customer feedback and create a summary report",
    "workflow": "full",
    "enable_retrieval": true
}
```

## Streaming

Set `stream: true` to receive real-time responses:
```json
{
    "message": "Tell me a story",
    "workflow": "plain",
    "stream": true
}
```

Streaming responses use Server-Sent Events (SSE) format with event types:
- `token`: Content chunks
- `node_start`: Workflow node started
- `node_complete`: Workflow node completed
- `usage`: Final usage statistics
- `error`: Error occurred

## Templates

Use pre-configured templates for common scenarios:
```json
{
    "message": "I need help with my order",
    "workflow_template": "customer_support"
}
```

Available templates:
- `customer_support`: Customer service with knowledge base
- `code_assistant`: Programming help with code tools
- `research_assistant`: Document research and analysis
- `general_chat`: General conversation
- `document_qa`: Document question answering
- `data_analyst`: Data analysis with computation tools


### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.chat_request import ChatRequest
from chatter_sdk.models.chat_response import ChatResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ChatApi(api_client)
    chat_request = {"message":"Write a Python function to calculate fibonacci numbers","workflow":"tools","stream":true} # ChatRequest | 

    try:
        # Chat
        api_response = await api_instance.chat_api_v1_chat_chat_post(chat_request)
        print("The response of ChatApi->chat_api_v1_chat_chat_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChatApi->chat_api_v1_chat_chat_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **chat_request** | [**ChatRequest**](ChatRequest.md)|  | 

### Return type

[**ChatResponse**](ChatResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **chat_with_template_api_v1_chat_template_template_name_post**
> ChatResponse chat_with_template_api_v1_chat_template_template_name_post(template_name, chat_request)

Chat With Template

Chat using a specific workflow template.
## Workflow Types

This endpoint supports multiple workflow types through the `workflow` parameter:

### Plain Chat (`plain`)
Basic conversation without tools or retrieval.
```json
{
    "message": "Hello, how are you?",
    "workflow": "plain"
}
```

### RAG Workflow (`rag`)
Retrieval-Augmented Generation with document search.
```json
{
    "message": "What are the latest sales figures?",
    "workflow": "rag",
    "enable_retrieval": true
}
```

### Tools Workflow (`tools`)
Function calling with available tools.
```json
{
    "message": "Calculate the square root of 144",
    "workflow": "tools"
}
```

### Full Workflow (`full`)
Combination of RAG and tools for complex tasks.
```json
{
    "message": "Find recent customer feedback and create a summary report",
    "workflow": "full",
    "enable_retrieval": true
}
```

## Streaming

Set `stream: true` to receive real-time responses:
```json
{
    "message": "Tell me a story",
    "workflow": "plain",
    "stream": true
}
```

Streaming responses use Server-Sent Events (SSE) format with event types:
- `token`: Content chunks
- `node_start`: Workflow node started
- `node_complete`: Workflow node completed
- `usage`: Final usage statistics
- `error`: Error occurred

## Templates

Use pre-configured templates for common scenarios:
```json
{
    "message": "I need help with my order",
    "workflow_template": "customer_support"
}
```

Available templates:
- `customer_support`: Customer service with knowledge base
- `code_assistant`: Programming help with code tools
- `research_assistant`: Document research and analysis
- `general_chat`: General conversation
- `document_qa`: Document question answering
- `data_analyst`: Data analysis with computation tools


### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.chat_request import ChatRequest
from chatter_sdk.models.chat_response import ChatResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ChatApi(api_client)
    template_name = 'template_name_example' # str | 
    chat_request = chatter_sdk.ChatRequest() # ChatRequest | 

    try:
        # Chat With Template
        api_response = await api_instance.chat_with_template_api_v1_chat_template_template_name_post(template_name, chat_request)
        print("The response of ChatApi->chat_with_template_api_v1_chat_template_template_name_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChatApi->chat_with_template_api_v1_chat_template_template_name_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **template_name** | **str**|  | 
 **chat_request** | [**ChatRequest**](ChatRequest.md)|  | 

### Return type

[**ChatResponse**](ChatResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_conversation_api_v1_chat_conversations_post**
> ConversationResponse create_conversation_api_v1_chat_conversations_post(conversation_create)

Create Conversation

Create a new conversation.

Create a new conversation with specified configuration
## Workflow Types

This endpoint supports multiple workflow types through the `workflow` parameter:

### Plain Chat (`plain`)
Basic conversation without tools or retrieval.
```json
{
    "message": "Hello, how are you?",
    "workflow": "plain"
}
```

### RAG Workflow (`rag`)
Retrieval-Augmented Generation with document search.
```json
{
    "message": "What are the latest sales figures?",
    "workflow": "rag",
    "enable_retrieval": true
}
```

### Tools Workflow (`tools`)
Function calling with available tools.
```json
{
    "message": "Calculate the square root of 144",
    "workflow": "tools"
}
```

### Full Workflow (`full`)
Combination of RAG and tools for complex tasks.
```json
{
    "message": "Find recent customer feedback and create a summary report",
    "workflow": "full",
    "enable_retrieval": true
}
```

## Streaming

Set `stream: true` to receive real-time responses:
```json
{
    "message": "Tell me a story",
    "workflow": "plain",
    "stream": true
}
```

Streaming responses use Server-Sent Events (SSE) format with event types:
- `token`: Content chunks
- `node_start`: Workflow node started
- `node_complete`: Workflow node completed
- `usage`: Final usage statistics
- `error`: Error occurred

## Templates

Use pre-configured templates for common scenarios:
```json
{
    "message": "I need help with my order",
    "workflow_template": "customer_support"
}
```

Available templates:
- `customer_support`: Customer service with knowledge base
- `code_assistant`: Programming help with code tools
- `research_assistant`: Document research and analysis
- `general_chat`: General conversation
- `document_qa`: Document question answering
- `data_analyst`: Data analysis with computation tools


### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.conversation_create import ConversationCreate
from chatter_sdk.models.conversation_response import ConversationResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ChatApi(api_client)
    conversation_create = {"title":"Help with Python","description":"Discussion about Python programming","llm_provider":"openai","llm_model":"gpt-4","temperature":0.7,"system_prompt":"You are a helpful Python programming assistant."} # ConversationCreate | 

    try:
        # Create Conversation
        api_response = await api_instance.create_conversation_api_v1_chat_conversations_post(conversation_create)
        print("The response of ChatApi->create_conversation_api_v1_chat_conversations_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChatApi->create_conversation_api_v1_chat_conversations_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **conversation_create** | [**ConversationCreate**](ConversationCreate.md)|  | 

### Return type

[**ConversationResponse**](ConversationResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_conversation_api_v1_chat_conversations_conversation_id_delete**
> ConversationDeleteResponse delete_conversation_api_v1_chat_conversations_conversation_id_delete(conversation_id)

Delete Conversation

Delete conversation.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.conversation_delete_response import ConversationDeleteResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ChatApi(api_client)
    conversation_id = 'conversation_id_example' # str | Conversation ID

    try:
        # Delete Conversation
        api_response = await api_instance.delete_conversation_api_v1_chat_conversations_conversation_id_delete(conversation_id)
        print("The response of ChatApi->delete_conversation_api_v1_chat_conversations_conversation_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChatApi->delete_conversation_api_v1_chat_conversations_conversation_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **conversation_id** | **str**| Conversation ID | 

### Return type

[**ConversationDeleteResponse**](ConversationDeleteResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_message_api_v1_chat_conversations_conversation_id_messages_message_id_delete**
> MessageDeleteResponse delete_message_api_v1_chat_conversations_conversation_id_messages_message_id_delete(conversation_id, message_id)

Delete Message

Delete a message from a conversation.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.message_delete_response import MessageDeleteResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ChatApi(api_client)
    conversation_id = 'conversation_id_example' # str | Conversation ID
    message_id = 'message_id_example' # str | Message ID

    try:
        # Delete Message
        api_response = await api_instance.delete_message_api_v1_chat_conversations_conversation_id_messages_message_id_delete(conversation_id, message_id)
        print("The response of ChatApi->delete_message_api_v1_chat_conversations_conversation_id_messages_message_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChatApi->delete_message_api_v1_chat_conversations_conversation_id_messages_message_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **conversation_id** | **str**| Conversation ID | 
 **message_id** | **str**| Message ID | 

### Return type

[**MessageDeleteResponse**](MessageDeleteResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_available_tools_api_v1_chat_tools_available_get**
> AvailableToolsResponse get_available_tools_api_v1_chat_tools_available_get()

Get Available Tools

Get list of available MCP tools.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.available_tools_response import AvailableToolsResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ChatApi(api_client)

    try:
        # Get Available Tools
        api_response = await api_instance.get_available_tools_api_v1_chat_tools_available_get()
        print("The response of ChatApi->get_available_tools_api_v1_chat_tools_available_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChatApi->get_available_tools_api_v1_chat_tools_available_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**AvailableToolsResponse**](AvailableToolsResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_conversation_api_v1_chat_conversations_conversation_id_get**
> ConversationWithMessages get_conversation_api_v1_chat_conversations_conversation_id_get(conversation_id, include_messages=include_messages)

Get Conversation

Get conversation details with optional messages.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.conversation_with_messages import ConversationWithMessages
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ChatApi(api_client)
    conversation_id = 'conversation_id_example' # str | Conversation ID
    include_messages = True # bool | Include messages in response (optional) (default to True)

    try:
        # Get Conversation
        api_response = await api_instance.get_conversation_api_v1_chat_conversations_conversation_id_get(conversation_id, include_messages=include_messages)
        print("The response of ChatApi->get_conversation_api_v1_chat_conversations_conversation_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChatApi->get_conversation_api_v1_chat_conversations_conversation_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **conversation_id** | **str**| Conversation ID | 
 **include_messages** | **bool**| Include messages in response | [optional] [default to True]

### Return type

[**ConversationWithMessages**](ConversationWithMessages.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_conversation_messages_api_v1_chat_conversations_conversation_id_messages_get**
> List[MessageResponse] get_conversation_messages_api_v1_chat_conversations_conversation_id_messages_get(conversation_id, limit=limit, offset=offset)

Get Conversation Messages

Get messages from a conversation.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.message_response import MessageResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ChatApi(api_client)
    conversation_id = 'conversation_id_example' # str | Conversation ID
    limit = 50 # int | Number of results per page (optional) (default to 50)
    offset = 0 # int | Number of results to skip (optional) (default to 0)

    try:
        # Get Conversation Messages
        api_response = await api_instance.get_conversation_messages_api_v1_chat_conversations_conversation_id_messages_get(conversation_id, limit=limit, offset=offset)
        print("The response of ChatApi->get_conversation_messages_api_v1_chat_conversations_conversation_id_messages_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChatApi->get_conversation_messages_api_v1_chat_conversations_conversation_id_messages_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **conversation_id** | **str**| Conversation ID | 
 **limit** | **int**| Number of results per page | [optional] [default to 50]
 **offset** | **int**| Number of results to skip | [optional] [default to 0]

### Return type

[**List[MessageResponse]**](MessageResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_mcp_status_api_v1_chat_mcp_status_get**
> McpStatusResponse get_mcp_status_api_v1_chat_mcp_status_get()

Get Mcp Status

Get MCP service status.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.mcp_status_response import McpStatusResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ChatApi(api_client)

    try:
        # Get Mcp Status
        api_response = await api_instance.get_mcp_status_api_v1_chat_mcp_status_get()
        print("The response of ChatApi->get_mcp_status_api_v1_chat_mcp_status_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChatApi->get_mcp_status_api_v1_chat_mcp_status_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**McpStatusResponse**](McpStatusResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_performance_stats_api_v1_chat_performance_stats_get**
> PerformanceStatsResponse get_performance_stats_api_v1_chat_performance_stats_get()

Get Performance Stats

Get workflow performance statistics.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.performance_stats_response import PerformanceStatsResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ChatApi(api_client)

    try:
        # Get Performance Stats
        api_response = await api_instance.get_performance_stats_api_v1_chat_performance_stats_get()
        print("The response of ChatApi->get_performance_stats_api_v1_chat_performance_stats_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChatApi->get_performance_stats_api_v1_chat_performance_stats_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**PerformanceStatsResponse**](PerformanceStatsResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_workflow_templates_api_v1_chat_templates_get**
> ChatterSchemasChatWorkflowTemplatesResponse get_workflow_templates_api_v1_chat_templates_get()

Get Workflow Templates

Get available workflow templates.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.chatter_schemas_chat_workflow_templates_response import ChatterSchemasChatWorkflowTemplatesResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ChatApi(api_client)

    try:
        # Get Workflow Templates
        api_response = await api_instance.get_workflow_templates_api_v1_chat_templates_get()
        print("The response of ChatApi->get_workflow_templates_api_v1_chat_templates_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChatApi->get_workflow_templates_api_v1_chat_templates_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**ChatterSchemasChatWorkflowTemplatesResponse**](ChatterSchemasChatWorkflowTemplatesResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_conversations_api_v1_chat_conversations_get**
> ConversationSearchResponse list_conversations_api_v1_chat_conversations_get(limit=limit, offset=offset)

List Conversations

List conversations for the current user.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.conversation_search_response import ConversationSearchResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ChatApi(api_client)
    limit = 20 # int | Number of results per page (optional) (default to 20)
    offset = 0 # int | Number of results to skip (optional) (default to 0)

    try:
        # List Conversations
        api_response = await api_instance.list_conversations_api_v1_chat_conversations_get(limit=limit, offset=offset)
        print("The response of ChatApi->list_conversations_api_v1_chat_conversations_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChatApi->list_conversations_api_v1_chat_conversations_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**| Number of results per page | [optional] [default to 20]
 **offset** | **int**| Number of results to skip | [optional] [default to 0]

### Return type

[**ConversationSearchResponse**](ConversationSearchResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **streaming_chat_api_v1_chat_streaming_post**
> object streaming_chat_api_v1_chat_streaming_post(chat_request)

Streaming Chat

Streaming chat endpoint supporting all workflow types.
## Workflow Types

This endpoint supports multiple workflow types through the `workflow` parameter:

### Plain Chat (`plain`)
Basic conversation without tools or retrieval.
```json
{
    "message": "Hello, how are you?",
    "workflow": "plain"
}
```

### RAG Workflow (`rag`)
Retrieval-Augmented Generation with document search.
```json
{
    "message": "What are the latest sales figures?",
    "workflow": "rag",
    "enable_retrieval": true
}
```

### Tools Workflow (`tools`)
Function calling with available tools.
```json
{
    "message": "Calculate the square root of 144",
    "workflow": "tools"
}
```

### Full Workflow (`full`)
Combination of RAG and tools for complex tasks.
```json
{
    "message": "Find recent customer feedback and create a summary report",
    "workflow": "full",
    "enable_retrieval": true
}
```

## Streaming

Set `stream: true` to receive real-time responses:
```json
{
    "message": "Tell me a story",
    "workflow": "plain",
    "stream": true
}
```

Streaming responses use Server-Sent Events (SSE) format with event types:
- `token`: Content chunks
- `node_start`: Workflow node started
- `node_complete`: Workflow node completed
- `usage`: Final usage statistics
- `error`: Error occurred

## Templates

Use pre-configured templates for common scenarios:
```json
{
    "message": "I need help with my order",
    "workflow_template": "customer_support"
}
```

Available templates:
- `customer_support`: Customer service with knowledge base
- `code_assistant`: Programming help with code tools
- `research_assistant`: Document research and analysis
- `general_chat`: General conversation
- `document_qa`: Document question answering
- `data_analyst`: Data analysis with computation tools


### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.chat_request import ChatRequest
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ChatApi(api_client)
    chat_request = chatter_sdk.ChatRequest() # ChatRequest | 

    try:
        # Streaming Chat
        api_response = await api_instance.streaming_chat_api_v1_chat_streaming_post(chat_request)
        print("The response of ChatApi->streaming_chat_api_v1_chat_streaming_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChatApi->streaming_chat_api_v1_chat_streaming_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **chat_request** | [**ChatRequest**](ChatRequest.md)|  | 

### Return type

**object**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json, text/event-stream

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Streaming chat response using Server-Sent Events |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_conversation_api_v1_chat_conversations_conversation_id_put**
> ConversationResponse update_conversation_api_v1_chat_conversations_conversation_id_put(conversation_id, conversation_update)

Update Conversation

Update conversation.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.conversation_response import ConversationResponse
from chatter_sdk.models.conversation_update import ConversationUpdate
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ChatApi(api_client)
    conversation_id = 'conversation_id_example' # str | Conversation ID
    conversation_update = chatter_sdk.ConversationUpdate() # ConversationUpdate | 

    try:
        # Update Conversation
        api_response = await api_instance.update_conversation_api_v1_chat_conversations_conversation_id_put(conversation_id, conversation_update)
        print("The response of ChatApi->update_conversation_api_v1_chat_conversations_conversation_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChatApi->update_conversation_api_v1_chat_conversations_conversation_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **conversation_id** | **str**| Conversation ID | 
 **conversation_update** | [**ConversationUpdate**](ConversationUpdate.md)|  | 

### Return type

[**ConversationResponse**](ConversationResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

