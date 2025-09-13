# chatter_sdk.ConversationsApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_conversation_api_v1_conversations_post**](ConversationsApi.md#create_conversation_api_v1_conversations_post) | **POST** /api/v1/conversations/ | Create Conversation
[**delete_conversation_api_v1_conversations_conversation_id_delete**](ConversationsApi.md#delete_conversation_api_v1_conversations_conversation_id_delete) | **DELETE** /api/v1/conversations/{conversation_id} | Delete Conversation
[**delete_message_api_v1_conversations_conversation_id_messages_message_id_delete**](ConversationsApi.md#delete_message_api_v1_conversations_conversation_id_messages_message_id_delete) | **DELETE** /api/v1/conversations/{conversation_id}/messages/{message_id} | Delete Message
[**get_conversation_api_v1_conversations_conversation_id_get**](ConversationsApi.md#get_conversation_api_v1_conversations_conversation_id_get) | **GET** /api/v1/conversations/{conversation_id} | Get Conversation
[**get_conversation_messages_api_v1_conversations_conversation_id_messages_get**](ConversationsApi.md#get_conversation_messages_api_v1_conversations_conversation_id_messages_get) | **GET** /api/v1/conversations/{conversation_id}/messages | Get Conversation Messages
[**list_conversations_api_v1_conversations_get**](ConversationsApi.md#list_conversations_api_v1_conversations_get) | **GET** /api/v1/conversations/ | List Conversations
[**update_conversation_api_v1_conversations_conversation_id_put**](ConversationsApi.md#update_conversation_api_v1_conversations_conversation_id_put) | **PUT** /api/v1/conversations/{conversation_id} | Update Conversation
[**update_message_rating_api_v1_conversations_conversation_id_messages_message_id_rating_patch**](ConversationsApi.md#update_message_rating_api_v1_conversations_conversation_id_messages_message_id_rating_patch) | **PATCH** /api/v1/conversations/{conversation_id}/messages/{message_id}/rating | Update Message Rating


# **create_conversation_api_v1_conversations_post**
> ConversationResponse create_conversation_api_v1_conversations_post(conversation_create)

Create Conversation

Create a new conversation.

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
    api_instance = chatter_sdk.ConversationsApi(api_client)
    conversation_create = chatter_sdk.ConversationCreate() # ConversationCreate | 

    try:
        # Create Conversation
        api_response = await api_instance.create_conversation_api_v1_conversations_post(conversation_create)
        print("The response of ConversationsApi->create_conversation_api_v1_conversations_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConversationsApi->create_conversation_api_v1_conversations_post: %s\n" % e)
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

# **delete_conversation_api_v1_conversations_conversation_id_delete**
> ConversationDeleteResponse delete_conversation_api_v1_conversations_conversation_id_delete(conversation_id)

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
    api_instance = chatter_sdk.ConversationsApi(api_client)
    conversation_id = 'conversation_id_example' # str | Conversation ID

    try:
        # Delete Conversation
        api_response = await api_instance.delete_conversation_api_v1_conversations_conversation_id_delete(conversation_id)
        print("The response of ConversationsApi->delete_conversation_api_v1_conversations_conversation_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConversationsApi->delete_conversation_api_v1_conversations_conversation_id_delete: %s\n" % e)
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

# **delete_message_api_v1_conversations_conversation_id_messages_message_id_delete**
> MessageDeleteResponse delete_message_api_v1_conversations_conversation_id_messages_message_id_delete(conversation_id, message_id)

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
    api_instance = chatter_sdk.ConversationsApi(api_client)
    conversation_id = 'conversation_id_example' # str | Conversation ID
    message_id = 'message_id_example' # str | Message ID

    try:
        # Delete Message
        api_response = await api_instance.delete_message_api_v1_conversations_conversation_id_messages_message_id_delete(conversation_id, message_id)
        print("The response of ConversationsApi->delete_message_api_v1_conversations_conversation_id_messages_message_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConversationsApi->delete_message_api_v1_conversations_conversation_id_messages_message_id_delete: %s\n" % e)
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

# **get_conversation_api_v1_conversations_conversation_id_get**
> ConversationWithMessages get_conversation_api_v1_conversations_conversation_id_get(conversation_id, include_messages=include_messages)

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
    api_instance = chatter_sdk.ConversationsApi(api_client)
    conversation_id = 'conversation_id_example' # str | Conversation ID
    include_messages = True # bool | Include messages in response (optional) (default to True)

    try:
        # Get Conversation
        api_response = await api_instance.get_conversation_api_v1_conversations_conversation_id_get(conversation_id, include_messages=include_messages)
        print("The response of ConversationsApi->get_conversation_api_v1_conversations_conversation_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConversationsApi->get_conversation_api_v1_conversations_conversation_id_get: %s\n" % e)
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

# **get_conversation_messages_api_v1_conversations_conversation_id_messages_get**
> List[MessageResponse] get_conversation_messages_api_v1_conversations_conversation_id_messages_get(conversation_id, limit=limit, offset=offset)

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
    api_instance = chatter_sdk.ConversationsApi(api_client)
    conversation_id = 'conversation_id_example' # str | Conversation ID
    limit = 50 # int | Number of results per page (optional) (default to 50)
    offset = 0 # int | Number of results to skip (optional) (default to 0)

    try:
        # Get Conversation Messages
        api_response = await api_instance.get_conversation_messages_api_v1_conversations_conversation_id_messages_get(conversation_id, limit=limit, offset=offset)
        print("The response of ConversationsApi->get_conversation_messages_api_v1_conversations_conversation_id_messages_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConversationsApi->get_conversation_messages_api_v1_conversations_conversation_id_messages_get: %s\n" % e)
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

# **list_conversations_api_v1_conversations_get**
> ConversationListResponse list_conversations_api_v1_conversations_get(status=status, llm_provider=llm_provider, llm_model=llm_model, tags=tags, enable_retrieval=enable_retrieval, limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order)

List Conversations

List conversations for the current user.

Args:
    status: Filter by conversation status
    llm_provider: Filter by LLM provider
    llm_model: Filter by LLM model
    tags: Filter by tags
    enable_retrieval: Filter by retrieval enabled status
    limit: Maximum number of results
    offset: Number of results to skip
    sort_by: Sort field
    sort_order: Sort order (asc/desc)
    current_user: Current authenticated user
    handler: Conversation resource handler

Returns:
    List of conversations with pagination info

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.conversation_list_response import ConversationListResponse
from chatter_sdk.models.conversation_status import ConversationStatus
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
    api_instance = chatter_sdk.ConversationsApi(api_client)
    status = chatter_sdk.ConversationStatus() # ConversationStatus | Filter by conversation status (optional)
    llm_provider = 'llm_provider_example' # str | Filter by LLM provider (optional)
    llm_model = 'llm_model_example' # str | Filter by LLM model (optional)
    tags = ['tags_example'] # List[str] | Filter by tags (optional)
    enable_retrieval = True # bool | Filter by retrieval enabled status (optional)
    limit = 50 # int | Maximum number of results (optional) (default to 50)
    offset = 0 # int | Number of results to skip (optional) (default to 0)
    sort_by = 'updated_at' # str | Sort field (optional) (default to 'updated_at')
    sort_order = 'desc' # str | Sort order (optional) (default to 'desc')

    try:
        # List Conversations
        api_response = await api_instance.list_conversations_api_v1_conversations_get(status=status, llm_provider=llm_provider, llm_model=llm_model, tags=tags, enable_retrieval=enable_retrieval, limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order)
        print("The response of ConversationsApi->list_conversations_api_v1_conversations_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConversationsApi->list_conversations_api_v1_conversations_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **status** | [**ConversationStatus**](.md)| Filter by conversation status | [optional] 
 **llm_provider** | **str**| Filter by LLM provider | [optional] 
 **llm_model** | **str**| Filter by LLM model | [optional] 
 **tags** | [**List[str]**](str.md)| Filter by tags | [optional] 
 **enable_retrieval** | **bool**| Filter by retrieval enabled status | [optional] 
 **limit** | **int**| Maximum number of results | [optional] [default to 50]
 **offset** | **int**| Number of results to skip | [optional] [default to 0]
 **sort_by** | **str**| Sort field | [optional] [default to &#39;updated_at&#39;]
 **sort_order** | **str**| Sort order | [optional] [default to &#39;desc&#39;]

### Return type

[**ConversationListResponse**](ConversationListResponse.md)

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

# **update_conversation_api_v1_conversations_conversation_id_put**
> ConversationResponse update_conversation_api_v1_conversations_conversation_id_put(conversation_id, conversation_update)

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
    api_instance = chatter_sdk.ConversationsApi(api_client)
    conversation_id = 'conversation_id_example' # str | Conversation ID
    conversation_update = chatter_sdk.ConversationUpdate() # ConversationUpdate | 

    try:
        # Update Conversation
        api_response = await api_instance.update_conversation_api_v1_conversations_conversation_id_put(conversation_id, conversation_update)
        print("The response of ConversationsApi->update_conversation_api_v1_conversations_conversation_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConversationsApi->update_conversation_api_v1_conversations_conversation_id_put: %s\n" % e)
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

# **update_message_rating_api_v1_conversations_conversation_id_messages_message_id_rating_patch**
> MessageRatingResponse update_message_rating_api_v1_conversations_conversation_id_messages_message_id_rating_patch(conversation_id, message_id, message_rating_update)

Update Message Rating

Update the rating for a message.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.message_rating_response import MessageRatingResponse
from chatter_sdk.models.message_rating_update import MessageRatingUpdate
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
    api_instance = chatter_sdk.ConversationsApi(api_client)
    conversation_id = 'conversation_id_example' # str | Conversation ID
    message_id = 'message_id_example' # str | Message ID
    message_rating_update = chatter_sdk.MessageRatingUpdate() # MessageRatingUpdate | 

    try:
        # Update Message Rating
        api_response = await api_instance.update_message_rating_api_v1_conversations_conversation_id_messages_message_id_rating_patch(conversation_id, message_id, message_rating_update)
        print("The response of ConversationsApi->update_message_rating_api_v1_conversations_conversation_id_messages_message_id_rating_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConversationsApi->update_message_rating_api_v1_conversations_conversation_id_messages_message_id_rating_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **conversation_id** | **str**| Conversation ID | 
 **message_id** | **str**| Message ID | 
 **message_rating_update** | [**MessageRatingUpdate**](MessageRatingUpdate.md)|  | 

### Return type

[**MessageRatingResponse**](MessageRatingResponse.md)

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

