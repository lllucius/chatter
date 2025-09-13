# chatter_sdk.ChatApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**chat_api_v1_chat_chat_post**](ChatApi.md#chat_api_v1_chat_chat_post) | **POST** /api/v1/chat/chat | Chat
[**chat_with_template_api_v1_chat_template_template_name_post**](ChatApi.md#chat_with_template_api_v1_chat_template_template_name_post) | **POST** /api/v1/chat/template/{template_name} | Chat With Template
[**get_available_tools_api_v1_chat_tools_available_get**](ChatApi.md#get_available_tools_api_v1_chat_tools_available_get) | **GET** /api/v1/chat/tools/available | Get Available Tools
[**get_mcp_status_api_v1_chat_mcp_status_get**](ChatApi.md#get_mcp_status_api_v1_chat_mcp_status_get) | **GET** /api/v1/chat/mcp/status | Get Mcp Status
[**get_performance_stats_api_v1_chat_performance_stats_get**](ChatApi.md#get_performance_stats_api_v1_chat_performance_stats_get) | **GET** /api/v1/chat/performance/stats | Get Performance Stats
[**get_workflow_templates_api_v1_chat_templates_get**](ChatApi.md#get_workflow_templates_api_v1_chat_templates_get) | **GET** /api/v1/chat/templates | Get Workflow Templates
[**streaming_chat_api_v1_chat_streaming_post**](ChatApi.md#streaming_chat_api_v1_chat_streaming_post) | **POST** /api/v1/chat/streaming | Streaming Chat


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

