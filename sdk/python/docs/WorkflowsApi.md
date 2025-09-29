# chatter_sdk.WorkflowsApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**configure_memory_settings_api_v1_workflows_memory_configure_post**](WorkflowsApi.md#configure_memory_settings_api_v1_workflows_memory_configure_post) | **POST** /api/v1/workflows/memory/configure | Configure Memory Settings
[**configure_tool_settings_api_v1_workflows_tools_configure_post**](WorkflowsApi.md#configure_tool_settings_api_v1_workflows_tools_configure_post) | **POST** /api/v1/workflows/tools/configure | Configure Tool Settings
[**create_workflow_definition_api_v1_workflows_definitions_post**](WorkflowsApi.md#create_workflow_definition_api_v1_workflows_definitions_post) | **POST** /api/v1/workflows/definitions | Create Workflow Definition
[**create_workflow_definition_from_template_api_v1_workflows_definitions_from_template_post**](WorkflowsApi.md#create_workflow_definition_from_template_api_v1_workflows_definitions_from_template_post) | **POST** /api/v1/workflows/definitions/from-template | Create Workflow Definition From Template
[**create_workflow_template_api_v1_workflows_templates_post**](WorkflowsApi.md#create_workflow_template_api_v1_workflows_templates_post) | **POST** /api/v1/workflows/templates | Create Workflow Template
[**delete_workflow_definition_api_v1_workflows_definitions_workflow_id_delete**](WorkflowsApi.md#delete_workflow_definition_api_v1_workflows_definitions_workflow_id_delete) | **DELETE** /api/v1/workflows/definitions/{workflow_id} | Delete Workflow Definition
[**delete_workflow_template_api_v1_workflows_templates_template_id_delete**](WorkflowsApi.md#delete_workflow_template_api_v1_workflows_templates_template_id_delete) | **DELETE** /api/v1/workflows/templates/{template_id} | Delete Workflow Template
[**execute_chat_workflow_api_v1_workflows_execute_chat_post**](WorkflowsApi.md#execute_chat_workflow_api_v1_workflows_execute_chat_post) | **POST** /api/v1/workflows/execute/chat | Execute Chat Workflow
[**execute_chat_workflow_streaming_api_v1_workflows_execute_chat_streaming_post**](WorkflowsApi.md#execute_chat_workflow_streaming_api_v1_workflows_execute_chat_streaming_post) | **POST** /api/v1/workflows/execute/chat/streaming | Execute Chat Workflow Streaming
[**execute_custom_workflow_api_v1_workflows_definitions_custom_execute_post**](WorkflowsApi.md#execute_custom_workflow_api_v1_workflows_definitions_custom_execute_post) | **POST** /api/v1/workflows/definitions/custom/execute | Execute Custom Workflow
[**execute_workflow_api_v1_workflows_definitions_workflow_id_execute_post**](WorkflowsApi.md#execute_workflow_api_v1_workflows_definitions_workflow_id_execute_post) | **POST** /api/v1/workflows/definitions/{workflow_id}/execute | Execute Workflow
[**get_modern_supported_node_types_api_v1_workflows_node_types_modern_get**](WorkflowsApi.md#get_modern_supported_node_types_api_v1_workflows_node_types_modern_get) | **GET** /api/v1/workflows/node-types/modern | Get Modern Supported Node Types
[**get_supported_node_types_api_v1_workflows_node_types_get**](WorkflowsApi.md#get_supported_node_types_api_v1_workflows_node_types_get) | **GET** /api/v1/workflows/node-types | Get Supported Node Types
[**get_workflow_analytics_api_v1_workflows_definitions_workflow_id_analytics_get**](WorkflowsApi.md#get_workflow_analytics_api_v1_workflows_definitions_workflow_id_analytics_get) | **GET** /api/v1/workflows/definitions/{workflow_id}/analytics | Get Workflow Analytics
[**get_workflow_defaults_api_v1_workflows_defaults_get**](WorkflowsApi.md#get_workflow_defaults_api_v1_workflows_defaults_get) | **GET** /api/v1/workflows/defaults | Get Workflow Defaults
[**get_workflow_definition_api_v1_workflows_definitions_workflow_id_get**](WorkflowsApi.md#get_workflow_definition_api_v1_workflows_definitions_workflow_id_get) | **GET** /api/v1/workflows/definitions/{workflow_id} | Get Workflow Definition
[**get_workflow_execution_details_api_v1_workflows_definitions_workflow_id_executions_execution_id_get**](WorkflowsApi.md#get_workflow_execution_details_api_v1_workflows_definitions_workflow_id_executions_execution_id_get) | **GET** /api/v1/workflows/definitions/{workflow_id}/executions/{execution_id} | Get Workflow Execution Details
[**get_workflow_execution_logs_api_v1_workflows_definitions_workflow_id_executions_execution_id_logs_get**](WorkflowsApi.md#get_workflow_execution_logs_api_v1_workflows_definitions_workflow_id_executions_execution_id_logs_get) | **GET** /api/v1/workflows/definitions/{workflow_id}/executions/{execution_id}/logs | Get Workflow Execution Logs
[**list_workflow_definitions_api_v1_workflows_definitions_get**](WorkflowsApi.md#list_workflow_definitions_api_v1_workflows_definitions_get) | **GET** /api/v1/workflows/definitions | List Workflow Definitions
[**list_workflow_executions_api_v1_workflows_definitions_workflow_id_executions_get**](WorkflowsApi.md#list_workflow_executions_api_v1_workflows_definitions_workflow_id_executions_get) | **GET** /api/v1/workflows/definitions/{workflow_id}/executions | List Workflow Executions
[**list_workflow_templates_api_v1_workflows_templates_get**](WorkflowsApi.md#list_workflow_templates_api_v1_workflows_templates_get) | **GET** /api/v1/workflows/templates | List Workflow Templates
[**update_workflow_definition_api_v1_workflows_definitions_workflow_id_put**](WorkflowsApi.md#update_workflow_definition_api_v1_workflows_definitions_workflow_id_put) | **PUT** /api/v1/workflows/definitions/{workflow_id} | Update Workflow Definition
[**update_workflow_template_api_v1_workflows_templates_template_id_put**](WorkflowsApi.md#update_workflow_template_api_v1_workflows_templates_template_id_put) | **PUT** /api/v1/workflows/templates/{template_id} | Update Workflow Template
[**validate_workflow_definition_api_v1_workflows_definitions_validate_post**](WorkflowsApi.md#validate_workflow_definition_api_v1_workflows_definitions_validate_post) | **POST** /api/v1/workflows/definitions/validate | Validate Workflow Definition


# **configure_memory_settings_api_v1_workflows_memory_configure_post**
> Dict[str, object] configure_memory_settings_api_v1_workflows_memory_configure_post(adaptive_mode=adaptive_mode, base_window_size=base_window_size, max_window_size=max_window_size, summary_strategy=summary_strategy)

Configure Memory Settings

Configure memory management settings for the user.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    adaptive_mode = True # bool |  (optional) (default to True)
    base_window_size = 10 # int |  (optional) (default to 10)
    max_window_size = 50 # int |  (optional) (default to 50)
    summary_strategy = 'intelligent' # str |  (optional) (default to 'intelligent')

    try:
        # Configure Memory Settings
        api_response = await api_instance.configure_memory_settings_api_v1_workflows_memory_configure_post(adaptive_mode=adaptive_mode, base_window_size=base_window_size, max_window_size=max_window_size, summary_strategy=summary_strategy)
        print("The response of WorkflowsApi->configure_memory_settings_api_v1_workflows_memory_configure_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->configure_memory_settings_api_v1_workflows_memory_configure_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **adaptive_mode** | **bool**|  | [optional] [default to True]
 **base_window_size** | **int**|  | [optional] [default to 10]
 **max_window_size** | **int**|  | [optional] [default to 50]
 **summary_strategy** | **str**|  | [optional] [default to &#39;intelligent&#39;]

### Return type

**Dict[str, object]**

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

# **configure_tool_settings_api_v1_workflows_tools_configure_post**
> Dict[str, object] configure_tool_settings_api_v1_workflows_tools_configure_post(max_total_calls=max_total_calls, max_consecutive_calls=max_consecutive_calls, recursion_strategy=recursion_strategy, enable_recursion_detection=enable_recursion_detection)

Configure Tool Settings

Configure tool execution settings for the user.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    max_total_calls = 10 # int |  (optional) (default to 10)
    max_consecutive_calls = 3 # int |  (optional) (default to 3)
    recursion_strategy = 'adaptive' # str |  (optional) (default to 'adaptive')
    enable_recursion_detection = True # bool |  (optional) (default to True)

    try:
        # Configure Tool Settings
        api_response = await api_instance.configure_tool_settings_api_v1_workflows_tools_configure_post(max_total_calls=max_total_calls, max_consecutive_calls=max_consecutive_calls, recursion_strategy=recursion_strategy, enable_recursion_detection=enable_recursion_detection)
        print("The response of WorkflowsApi->configure_tool_settings_api_v1_workflows_tools_configure_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->configure_tool_settings_api_v1_workflows_tools_configure_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **max_total_calls** | **int**|  | [optional] [default to 10]
 **max_consecutive_calls** | **int**|  | [optional] [default to 3]
 **recursion_strategy** | **str**|  | [optional] [default to &#39;adaptive&#39;]
 **enable_recursion_detection** | **bool**|  | [optional] [default to True]

### Return type

**Dict[str, object]**

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

# **create_workflow_definition_api_v1_workflows_definitions_post**
> WorkflowDefinitionResponse create_workflow_definition_api_v1_workflows_definitions_post(workflow_definition_create)

Create Workflow Definition

Create a new workflow definition.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_definition_create import WorkflowDefinitionCreate
from chatter_sdk.models.workflow_definition_response import WorkflowDefinitionResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    workflow_definition_create = chatter_sdk.WorkflowDefinitionCreate() # WorkflowDefinitionCreate | 

    try:
        # Create Workflow Definition
        api_response = await api_instance.create_workflow_definition_api_v1_workflows_definitions_post(workflow_definition_create)
        print("The response of WorkflowsApi->create_workflow_definition_api_v1_workflows_definitions_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->create_workflow_definition_api_v1_workflows_definitions_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_definition_create** | [**WorkflowDefinitionCreate**](WorkflowDefinitionCreate.md)|  | 

### Return type

[**WorkflowDefinitionResponse**](WorkflowDefinitionResponse.md)

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

# **create_workflow_definition_from_template_api_v1_workflows_definitions_from_template_post**
> WorkflowDefinitionResponse create_workflow_definition_from_template_api_v1_workflows_definitions_from_template_post(workflow_definition_from_template_request)

Create Workflow Definition From Template

Create a workflow definition from a template.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_definition_from_template_request import WorkflowDefinitionFromTemplateRequest
from chatter_sdk.models.workflow_definition_response import WorkflowDefinitionResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    workflow_definition_from_template_request = chatter_sdk.WorkflowDefinitionFromTemplateRequest() # WorkflowDefinitionFromTemplateRequest | 

    try:
        # Create Workflow Definition From Template
        api_response = await api_instance.create_workflow_definition_from_template_api_v1_workflows_definitions_from_template_post(workflow_definition_from_template_request)
        print("The response of WorkflowsApi->create_workflow_definition_from_template_api_v1_workflows_definitions_from_template_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->create_workflow_definition_from_template_api_v1_workflows_definitions_from_template_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_definition_from_template_request** | [**WorkflowDefinitionFromTemplateRequest**](WorkflowDefinitionFromTemplateRequest.md)|  | 

### Return type

[**WorkflowDefinitionResponse**](WorkflowDefinitionResponse.md)

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

# **create_workflow_template_api_v1_workflows_templates_post**
> WorkflowTemplateResponse create_workflow_template_api_v1_workflows_templates_post(workflow_template_create)

Create Workflow Template

Create a new workflow template.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_template_create import WorkflowTemplateCreate
from chatter_sdk.models.workflow_template_response import WorkflowTemplateResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    workflow_template_create = chatter_sdk.WorkflowTemplateCreate() # WorkflowTemplateCreate | 

    try:
        # Create Workflow Template
        api_response = await api_instance.create_workflow_template_api_v1_workflows_templates_post(workflow_template_create)
        print("The response of WorkflowsApi->create_workflow_template_api_v1_workflows_templates_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->create_workflow_template_api_v1_workflows_templates_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_template_create** | [**WorkflowTemplateCreate**](WorkflowTemplateCreate.md)|  | 

### Return type

[**WorkflowTemplateResponse**](WorkflowTemplateResponse.md)

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

# **delete_workflow_definition_api_v1_workflows_definitions_workflow_id_delete**
> WorkflowDeleteResponse delete_workflow_definition_api_v1_workflows_definitions_workflow_id_delete(workflow_id)

Delete Workflow Definition

Delete a workflow definition.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_delete_response import WorkflowDeleteResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    workflow_id = 'workflow_id_example' # str | Workflow ID

    try:
        # Delete Workflow Definition
        api_response = await api_instance.delete_workflow_definition_api_v1_workflows_definitions_workflow_id_delete(workflow_id)
        print("The response of WorkflowsApi->delete_workflow_definition_api_v1_workflows_definitions_workflow_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->delete_workflow_definition_api_v1_workflows_definitions_workflow_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_id** | **str**| Workflow ID | 

### Return type

[**WorkflowDeleteResponse**](WorkflowDeleteResponse.md)

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

# **delete_workflow_template_api_v1_workflows_templates_template_id_delete**
> WorkflowDeleteResponse delete_workflow_template_api_v1_workflows_templates_template_id_delete(template_id)

Delete Workflow Template

Delete a workflow template.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_delete_response import WorkflowDeleteResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    template_id = 'template_id_example' # str | 

    try:
        # Delete Workflow Template
        api_response = await api_instance.delete_workflow_template_api_v1_workflows_templates_template_id_delete(template_id)
        print("The response of WorkflowsApi->delete_workflow_template_api_v1_workflows_templates_template_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->delete_workflow_template_api_v1_workflows_templates_template_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **template_id** | **str**|  | 

### Return type

[**WorkflowDeleteResponse**](WorkflowDeleteResponse.md)

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

# **execute_chat_workflow_api_v1_workflows_execute_chat_post**
> ChatResponse execute_chat_workflow_api_v1_workflows_execute_chat_post(chat_workflow_request)

Execute Chat Workflow

Execute chat using dynamically built workflow.
## Dynamic Workflow Configuration

This endpoint supports dynamic workflow configuration through capability flags:

### Basic Chat
Simple conversation without tools or retrieval.
```json
{
    "message": "Hello, how are you?",
    "enable_retrieval": false,
    "enable_tools": false
}
```

### Retrieval-Augmented Generation
Document search and retrieval capabilities.
```json
{
    "message": "What are the latest sales figures?",
    "enable_retrieval": true,
    "enable_tools": false
}
```

### Tool-Enhanced Workflow
Function calling with available tools.
```json
{
    "message": "Calculate the square root of 144",
    "enable_retrieval": false,
    "enable_tools": true
}
```

### Full-Featured Workflow
Combination of retrieval and tools for complex tasks.
```json
{
    "message": "Find recent customer feedback and create a summary report",
    "enable_retrieval": true,
    "enable_tools": true
}
```

## Streaming

Set `stream: true` to receive real-time responses:
```json
{
    "message": "Tell me a story",
    "enable_retrieval": false,
    "enable_tools": false,
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
from chatter_sdk.models.chat_response import ChatResponse
from chatter_sdk.models.chat_workflow_request import ChatWorkflowRequest
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    chat_workflow_request = chatter_sdk.ChatWorkflowRequest() # ChatWorkflowRequest | 

    try:
        # Execute Chat Workflow
        api_response = await api_instance.execute_chat_workflow_api_v1_workflows_execute_chat_post(chat_workflow_request)
        print("The response of WorkflowsApi->execute_chat_workflow_api_v1_workflows_execute_chat_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->execute_chat_workflow_api_v1_workflows_execute_chat_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **chat_workflow_request** | [**ChatWorkflowRequest**](ChatWorkflowRequest.md)|  | 

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

# **execute_chat_workflow_streaming_api_v1_workflows_execute_chat_streaming_post**
> object execute_chat_workflow_streaming_api_v1_workflows_execute_chat_streaming_post(chat_workflow_request)

Execute Chat Workflow Streaming

Execute chat using dynamically built workflow with streaming.
## Dynamic Workflow Configuration

This endpoint supports dynamic workflow configuration through capability flags:

### Basic Chat
Simple conversation without tools or retrieval.
```json
{
    "message": "Hello, how are you?",
    "enable_retrieval": false,
    "enable_tools": false
}
```

### Retrieval-Augmented Generation
Document search and retrieval capabilities.
```json
{
    "message": "What are the latest sales figures?",
    "enable_retrieval": true,
    "enable_tools": false
}
```

### Tool-Enhanced Workflow
Function calling with available tools.
```json
{
    "message": "Calculate the square root of 144",
    "enable_retrieval": false,
    "enable_tools": true
}
```

### Full-Featured Workflow
Combination of retrieval and tools for complex tasks.
```json
{
    "message": "Find recent customer feedback and create a summary report",
    "enable_retrieval": true,
    "enable_tools": true
}
```

## Streaming

Set `stream: true` to receive real-time responses:
```json
{
    "message": "Tell me a story",
    "enable_retrieval": false,
    "enable_tools": false,
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
from chatter_sdk.models.chat_workflow_request import ChatWorkflowRequest
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    chat_workflow_request = chatter_sdk.ChatWorkflowRequest() # ChatWorkflowRequest | 

    try:
        # Execute Chat Workflow Streaming
        api_response = await api_instance.execute_chat_workflow_streaming_api_v1_workflows_execute_chat_streaming_post(chat_workflow_request)
        print("The response of WorkflowsApi->execute_chat_workflow_streaming_api_v1_workflows_execute_chat_streaming_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->execute_chat_workflow_streaming_api_v1_workflows_execute_chat_streaming_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **chat_workflow_request** | [**ChatWorkflowRequest**](ChatWorkflowRequest.md)|  | 

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
**200** | Streaming chat response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **execute_custom_workflow_api_v1_workflows_definitions_custom_execute_post**
> Dict[str, object] execute_custom_workflow_api_v1_workflows_definitions_custom_execute_post(message, body_execute_custom_workflow_api_v1_workflows_definitions_custom_execute_post, entry_point=entry_point, provider=provider, model=model, conversation_id=conversation_id)

Execute Custom Workflow

Execute a custom workflow definition using the modern system.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.body_execute_custom_workflow_api_v1_workflows_definitions_custom_execute_post import BodyExecuteCustomWorkflowApiV1WorkflowsDefinitionsCustomExecutePost
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    message = 'message_example' # str | 
    body_execute_custom_workflow_api_v1_workflows_definitions_custom_execute_post = chatter_sdk.BodyExecuteCustomWorkflowApiV1WorkflowsDefinitionsCustomExecutePost() # BodyExecuteCustomWorkflowApiV1WorkflowsDefinitionsCustomExecutePost | 
    entry_point = 'entry_point_example' # str |  (optional)
    provider = 'openai' # str |  (optional) (default to 'openai')
    model = 'gpt-4' # str |  (optional) (default to 'gpt-4')
    conversation_id = 'conversation_id_example' # str |  (optional)

    try:
        # Execute Custom Workflow
        api_response = await api_instance.execute_custom_workflow_api_v1_workflows_definitions_custom_execute_post(message, body_execute_custom_workflow_api_v1_workflows_definitions_custom_execute_post, entry_point=entry_point, provider=provider, model=model, conversation_id=conversation_id)
        print("The response of WorkflowsApi->execute_custom_workflow_api_v1_workflows_definitions_custom_execute_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->execute_custom_workflow_api_v1_workflows_definitions_custom_execute_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **message** | **str**|  | 
 **body_execute_custom_workflow_api_v1_workflows_definitions_custom_execute_post** | [**BodyExecuteCustomWorkflowApiV1WorkflowsDefinitionsCustomExecutePost**](BodyExecuteCustomWorkflowApiV1WorkflowsDefinitionsCustomExecutePost.md)|  | 
 **entry_point** | **str**|  | [optional] 
 **provider** | **str**|  | [optional] [default to &#39;openai&#39;]
 **model** | **str**|  | [optional] [default to &#39;gpt-4&#39;]
 **conversation_id** | **str**|  | [optional] 

### Return type

**Dict[str, object]**

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

# **execute_workflow_api_v1_workflows_definitions_workflow_id_execute_post**
> WorkflowExecutionResponse execute_workflow_api_v1_workflows_definitions_workflow_id_execute_post(workflow_id, workflow_execution_request)

Execute Workflow

Execute a workflow definition.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_execution_request import WorkflowExecutionRequest
from chatter_sdk.models.workflow_execution_response import WorkflowExecutionResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    workflow_id = 'workflow_id_example' # str | Workflow ID
    workflow_execution_request = chatter_sdk.WorkflowExecutionRequest() # WorkflowExecutionRequest | 

    try:
        # Execute Workflow
        api_response = await api_instance.execute_workflow_api_v1_workflows_definitions_workflow_id_execute_post(workflow_id, workflow_execution_request)
        print("The response of WorkflowsApi->execute_workflow_api_v1_workflows_definitions_workflow_id_execute_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->execute_workflow_api_v1_workflows_definitions_workflow_id_execute_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_id** | **str**| Workflow ID | 
 **workflow_execution_request** | [**WorkflowExecutionRequest**](WorkflowExecutionRequest.md)|  | 

### Return type

[**WorkflowExecutionResponse**](WorkflowExecutionResponse.md)

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

# **get_modern_supported_node_types_api_v1_workflows_node_types_modern_get**
> Dict[str, object] get_modern_supported_node_types_api_v1_workflows_node_types_modern_get()

Get Modern Supported Node Types

Get supported node types from the modern workflow system.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)

    try:
        # Get Modern Supported Node Types
        api_response = await api_instance.get_modern_supported_node_types_api_v1_workflows_node_types_modern_get()
        print("The response of WorkflowsApi->get_modern_supported_node_types_api_v1_workflows_node_types_modern_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->get_modern_supported_node_types_api_v1_workflows_node_types_modern_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**Dict[str, object]**

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

# **get_supported_node_types_api_v1_workflows_node_types_get**
> List[NodeTypeResponse] get_supported_node_types_api_v1_workflows_node_types_get()

Get Supported Node Types

Get list of supported workflow node types.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.node_type_response import NodeTypeResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)

    try:
        # Get Supported Node Types
        api_response = await api_instance.get_supported_node_types_api_v1_workflows_node_types_get()
        print("The response of WorkflowsApi->get_supported_node_types_api_v1_workflows_node_types_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->get_supported_node_types_api_v1_workflows_node_types_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[NodeTypeResponse]**](NodeTypeResponse.md)

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

# **get_workflow_analytics_api_v1_workflows_definitions_workflow_id_analytics_get**
> WorkflowAnalyticsResponse get_workflow_analytics_api_v1_workflows_definitions_workflow_id_analytics_get(workflow_id)

Get Workflow Analytics

Get analytics for a specific workflow definition.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_analytics_response import WorkflowAnalyticsResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    workflow_id = 'workflow_id_example' # str | Workflow ID

    try:
        # Get Workflow Analytics
        api_response = await api_instance.get_workflow_analytics_api_v1_workflows_definitions_workflow_id_analytics_get(workflow_id)
        print("The response of WorkflowsApi->get_workflow_analytics_api_v1_workflows_definitions_workflow_id_analytics_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->get_workflow_analytics_api_v1_workflows_definitions_workflow_id_analytics_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_id** | **str**| Workflow ID | 

### Return type

[**WorkflowAnalyticsResponse**](WorkflowAnalyticsResponse.md)

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

# **get_workflow_defaults_api_v1_workflows_defaults_get**
> Dict[str, object] get_workflow_defaults_api_v1_workflows_defaults_get(node_type=node_type)

Get Workflow Defaults

Get workflow defaults from profiles, models, and prompts.

Args:
    node_type: Optional specific node type to get defaults for
    current_user: Current authenticated user
    defaults_service: Workflow defaults service
    
Returns:
    Dictionary containing default configurations

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    node_type = 'node_type_example' # str |  (optional)

    try:
        # Get Workflow Defaults
        api_response = await api_instance.get_workflow_defaults_api_v1_workflows_defaults_get(node_type=node_type)
        print("The response of WorkflowsApi->get_workflow_defaults_api_v1_workflows_defaults_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->get_workflow_defaults_api_v1_workflows_defaults_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **node_type** | **str**|  | [optional] 

### Return type

**Dict[str, object]**

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

# **get_workflow_definition_api_v1_workflows_definitions_workflow_id_get**
> WorkflowDefinitionResponse get_workflow_definition_api_v1_workflows_definitions_workflow_id_get(workflow_id)

Get Workflow Definition

Get a specific workflow definition.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_definition_response import WorkflowDefinitionResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    workflow_id = 'workflow_id_example' # str | Workflow ID

    try:
        # Get Workflow Definition
        api_response = await api_instance.get_workflow_definition_api_v1_workflows_definitions_workflow_id_get(workflow_id)
        print("The response of WorkflowsApi->get_workflow_definition_api_v1_workflows_definitions_workflow_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->get_workflow_definition_api_v1_workflows_definitions_workflow_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_id** | **str**| Workflow ID | 

### Return type

[**WorkflowDefinitionResponse**](WorkflowDefinitionResponse.md)

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

# **get_workflow_execution_details_api_v1_workflows_definitions_workflow_id_executions_execution_id_get**
> DetailedWorkflowExecutionResponse get_workflow_execution_details_api_v1_workflows_definitions_workflow_id_executions_execution_id_get(workflow_id, execution_id)

Get Workflow Execution Details

Get detailed information about a specific workflow execution.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.detailed_workflow_execution_response import DetailedWorkflowExecutionResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    workflow_id = 'workflow_id_example' # str | Workflow ID
    execution_id = 'execution_id_example' # str | 

    try:
        # Get Workflow Execution Details
        api_response = await api_instance.get_workflow_execution_details_api_v1_workflows_definitions_workflow_id_executions_execution_id_get(workflow_id, execution_id)
        print("The response of WorkflowsApi->get_workflow_execution_details_api_v1_workflows_definitions_workflow_id_executions_execution_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->get_workflow_execution_details_api_v1_workflows_definitions_workflow_id_executions_execution_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_id** | **str**| Workflow ID | 
 **execution_id** | **str**|  | 

### Return type

[**DetailedWorkflowExecutionResponse**](DetailedWorkflowExecutionResponse.md)

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

# **get_workflow_execution_logs_api_v1_workflows_definitions_workflow_id_executions_execution_id_logs_get**
> List[Dict[str, object]] get_workflow_execution_logs_api_v1_workflows_definitions_workflow_id_executions_execution_id_logs_get(workflow_id, execution_id, log_level=log_level, limit=limit)

Get Workflow Execution Logs

Get execution logs for a specific workflow execution.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    workflow_id = 'workflow_id_example' # str | Workflow ID
    execution_id = 'execution_id_example' # str | 
    log_level = 'log_level_example' # str |  (optional)
    limit = 1000 # int |  (optional) (default to 1000)

    try:
        # Get Workflow Execution Logs
        api_response = await api_instance.get_workflow_execution_logs_api_v1_workflows_definitions_workflow_id_executions_execution_id_logs_get(workflow_id, execution_id, log_level=log_level, limit=limit)
        print("The response of WorkflowsApi->get_workflow_execution_logs_api_v1_workflows_definitions_workflow_id_executions_execution_id_logs_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->get_workflow_execution_logs_api_v1_workflows_definitions_workflow_id_executions_execution_id_logs_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_id** | **str**| Workflow ID | 
 **execution_id** | **str**|  | 
 **log_level** | **str**|  | [optional] 
 **limit** | **int**|  | [optional] [default to 1000]

### Return type

**List[Dict[str, object]]**

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

# **list_workflow_definitions_api_v1_workflows_definitions_get**
> WorkflowDefinitionsResponse list_workflow_definitions_api_v1_workflows_definitions_get()

List Workflow Definitions

List all workflow definitions for the current user.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_definitions_response import WorkflowDefinitionsResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)

    try:
        # List Workflow Definitions
        api_response = await api_instance.list_workflow_definitions_api_v1_workflows_definitions_get()
        print("The response of WorkflowsApi->list_workflow_definitions_api_v1_workflows_definitions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->list_workflow_definitions_api_v1_workflows_definitions_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**WorkflowDefinitionsResponse**](WorkflowDefinitionsResponse.md)

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

# **list_workflow_executions_api_v1_workflows_definitions_workflow_id_executions_get**
> List[WorkflowExecutionResponse] list_workflow_executions_api_v1_workflows_definitions_workflow_id_executions_get(workflow_id)

List Workflow Executions

List executions for a workflow definition.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_execution_response import WorkflowExecutionResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    workflow_id = 'workflow_id_example' # str | Workflow ID

    try:
        # List Workflow Executions
        api_response = await api_instance.list_workflow_executions_api_v1_workflows_definitions_workflow_id_executions_get(workflow_id)
        print("The response of WorkflowsApi->list_workflow_executions_api_v1_workflows_definitions_workflow_id_executions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->list_workflow_executions_api_v1_workflows_definitions_workflow_id_executions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_id** | **str**| Workflow ID | 

### Return type

[**List[WorkflowExecutionResponse]**](WorkflowExecutionResponse.md)

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

# **list_workflow_templates_api_v1_workflows_templates_get**
> WorkflowTemplatesResponse list_workflow_templates_api_v1_workflows_templates_get()

List Workflow Templates

List all workflow templates accessible to the current user.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_templates_response import WorkflowTemplatesResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)

    try:
        # List Workflow Templates
        api_response = await api_instance.list_workflow_templates_api_v1_workflows_templates_get()
        print("The response of WorkflowsApi->list_workflow_templates_api_v1_workflows_templates_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->list_workflow_templates_api_v1_workflows_templates_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**WorkflowTemplatesResponse**](WorkflowTemplatesResponse.md)

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

# **update_workflow_definition_api_v1_workflows_definitions_workflow_id_put**
> WorkflowDefinitionResponse update_workflow_definition_api_v1_workflows_definitions_workflow_id_put(workflow_id, workflow_definition_update)

Update Workflow Definition

Update a workflow definition.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_definition_response import WorkflowDefinitionResponse
from chatter_sdk.models.workflow_definition_update import WorkflowDefinitionUpdate
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    workflow_id = 'workflow_id_example' # str | Workflow ID
    workflow_definition_update = chatter_sdk.WorkflowDefinitionUpdate() # WorkflowDefinitionUpdate | 

    try:
        # Update Workflow Definition
        api_response = await api_instance.update_workflow_definition_api_v1_workflows_definitions_workflow_id_put(workflow_id, workflow_definition_update)
        print("The response of WorkflowsApi->update_workflow_definition_api_v1_workflows_definitions_workflow_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->update_workflow_definition_api_v1_workflows_definitions_workflow_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_id** | **str**| Workflow ID | 
 **workflow_definition_update** | [**WorkflowDefinitionUpdate**](WorkflowDefinitionUpdate.md)|  | 

### Return type

[**WorkflowDefinitionResponse**](WorkflowDefinitionResponse.md)

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

# **update_workflow_template_api_v1_workflows_templates_template_id_put**
> WorkflowTemplateResponse update_workflow_template_api_v1_workflows_templates_template_id_put(template_id, workflow_template_update)

Update Workflow Template

Update a workflow template.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.workflow_template_response import WorkflowTemplateResponse
from chatter_sdk.models.workflow_template_update import WorkflowTemplateUpdate
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    template_id = 'template_id_example' # str | 
    workflow_template_update = chatter_sdk.WorkflowTemplateUpdate() # WorkflowTemplateUpdate | 

    try:
        # Update Workflow Template
        api_response = await api_instance.update_workflow_template_api_v1_workflows_templates_template_id_put(template_id, workflow_template_update)
        print("The response of WorkflowsApi->update_workflow_template_api_v1_workflows_templates_template_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->update_workflow_template_api_v1_workflows_templates_template_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **template_id** | **str**|  | 
 **workflow_template_update** | [**WorkflowTemplateUpdate**](WorkflowTemplateUpdate.md)|  | 

### Return type

[**WorkflowTemplateResponse**](WorkflowTemplateResponse.md)

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

# **validate_workflow_definition_api_v1_workflows_definitions_validate_post**
> WorkflowValidationResponse validate_workflow_definition_api_v1_workflows_definitions_validate_post(request)

Validate Workflow Definition

Validate a workflow definition - supports both legacy and modern formats.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.request import Request
from chatter_sdk.models.workflow_validation_response import WorkflowValidationResponse
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
    api_instance = chatter_sdk.WorkflowsApi(api_client)
    request = chatter_sdk.Request() # Request | 

    try:
        # Validate Workflow Definition
        api_response = await api_instance.validate_workflow_definition_api_v1_workflows_definitions_validate_post(request)
        print("The response of WorkflowsApi->validate_workflow_definition_api_v1_workflows_definitions_validate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkflowsApi->validate_workflow_definition_api_v1_workflows_definitions_validate_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request** | [**Request**](Request.md)|  | 

### Return type

[**WorkflowValidationResponse**](WorkflowValidationResponse.md)

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

